# Image-sharing-api
a small-scale REST API that supports an image-sharing application using Python

## Database
Azure Database for PostgreSQL [Flexible Server documentation](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-deploy-on-azure-free-account)
- Create an Azure PostgreSQL resource on Azure portal.
- Update settings.py file with database credentials.

````
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',           # The name of the database
        'USER': 'myuser',         # Your PostgreSQL username
        'PASSWORD': 'mypassword', # Your PostgreSQL password
        'HOST': 'localhost',      # Set to 'localhost' if PostgreSQL is running locally
        'PORT': '5432',           # Default PostgreSQL port
    }
}
````

- Run `python manage.py migrate`

## Database Schema 
View only link to database schema designs
https://drawsql.app/teams/image-sharing-api/diagrams/image-sharing-api
