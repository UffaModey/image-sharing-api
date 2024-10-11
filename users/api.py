# Third Party Stuff
from rest_framework import status, viewsets, permissions

from rest_framework.permissions import AllowAny

from .models import User
from .serializers import UserSerializer
from .utils.pagination import UsersPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('posts', 'followings', 'followers').all()
    serializer_class = UserSerializer
    pagination_class= UsersPagination


    def get_permissions(self):
        if self.action == 'create':  # Allow anyone to register
            self.permission_classes = [AllowAny]
        else:  # All other actions require authentication
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()
