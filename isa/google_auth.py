# Standard Library Imports
import json
import requests
from urllib.parse import urljoin

# Django and Django Rest Framework Imports
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

# Third-Party Package Imports
from password_generator import PasswordGenerator
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# Project-Specific Imports
User = get_user_model()


class LoginPage(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pages/login.html",
            {
                "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            },
        )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client


class GoogleLoginCallback(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Endpoint to handle Google OAuth callback and authenticate user in DRF app.
        """
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "No authorization code provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Exchange authorization code for access token
        token_data = self.get_google_token_data(code, request)
        token_response = self.get_google_token(token_data)

        if token_response.status_code != 200:
            return Response(
                {"error": "Failed to obtain tokens from Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_response.json().get("access_token")
        if not access_token:
            return Response(
                {"error": "No access token received from Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch user info from Google
        user_info = self.get_google_user_info(access_token)
        if not user_info:
            return Response(
                {"error": "Failed to fetch user info from Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create a user in your system and obtain a JWT token for the user
        user_jwt_token_response = self.get_or_create_user_with_jwt_token(user_info)

        if user_jwt_token_response.status_code != 200:
            return Response(
                {"error": "Failed to obtain JWT token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(user_jwt_token_response.json(), status=status.HTTP_200_OK)

    def get_google_token_data(self, code, request):
        """
        Prepare the data for exchanging the Google authorization code for an access token.
        """
        return {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": urljoin(
                request.build_absolute_uri("/"), "api/v1/auth/google/callback/"
            ),
            "grant_type": "authorization_code",
        }

    def get_google_token(self, token_data):
        """
        Request an access token from Google.
        """
        token_url = "https://oauth2.googleapis.com/token"
        return requests.post(token_url, data=token_data)

    def get_google_user_info(self, access_token):
        """
        Fetch the user info from Google using the access token.
        """
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        return (
            user_info_response.json() if user_info_response.status_code == 200 else None
        )

    def get_or_create_user_with_jwt_token(self, user_info):
        """
        Create or retrieve a user from the database using Google user information.
        """
        email = user_info.get("email")
        first_name = user_info.get("given_name")
        last_name = user_info.get("family_name")
        try:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"{first_name}{last_name}",  # Set email as username (if you want to use email as username)
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
        except Exception as e:
            raise {"message": f"Unable to get or create user: {e}"}

        password = PasswordGenerator().generate()
        user.set_password(password)
        user.save()

        # Request a JWT token for the authenticated user.

        url = "http://127.0.0.1:8000/api/token/"
        payload = json.dumps({"username": user.username, "password": password})
        headers = {"Content-Type": "application/json"}
        return requests.post(url, headers=headers, data=payload)
