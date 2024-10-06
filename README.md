# Image-sharing-api
a small-scale REST API that supports an image-sharing application using Python

## API Documentation
API reference doc on Postman 

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


## Linting and code formatting

## Database query optimization
- use select_related to manage database queries with many to one relationship

## Code Constraints
- Like models: Every `Like` object must be unique for the `liked_by` and `post` fields. This means that a post can only be liked once by a user.
  -  Add a `UniqueConstraint` constraint in the model's Meta class to ensure that each combination of `post` and `liked_by` is unique, meaning a user can only like a post once.
This will prevent duplicate likes and enforce the uniqueness at the database level.
- Follow models: Every `Follow` object must be unique for the `created_by` and `following` fields. This means that a user cannot follow themselves. 
  - Add a `UniqueConstraint` constraint in the model's Meta class to ensure that each combination of `created_by` and `following` is unique.
This will enforce the uniqueness at the database level.
- 

## Authentication
using Simple JWT for DRF. Increase the token life span.