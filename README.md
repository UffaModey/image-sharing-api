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

The goal is to optimize the database usage for speed and to limit the number of queries that are made to the db per request.
### Profile queries
The following methods were used to review queries and monitor database usage. 
- To find out what queries are executed and what they are costing.
```
>>> from django.db import connection
>>> connection.queries
```

- Use `QuerySet.explain()` to understand how specific `QuerySets` are executed by the database.

- [Django Debug Toolbar](https://pypi.org/project/django-debug-toolbar/)
  - Display various debug information about the current request/response.
  - [Installation guide](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)
  - Install [ModHeader](https://modheader.com/) browser extension to authenticate API requests on the browser.

### Standard DB optimization techniques
- Indexes were used for all `filter()` queries to  speed up lookups.
- Appropriate use of field types in database models.
- 

### Do database work in the database rather than in Python

### Retrieve everything at once if you know you will need it
- To reduce the number of database queries, and increase the performance of the api, prefetch_related was used 
to manage database queries with many-to-one relationship.
- API endpoint - http://127.0.0.1:8000/user/
  - reference to previous code version with 57 DB queries to list 8 users  in 1678.49 ms (54 queries were similar).
The number of queries increased with the number of users in the DB.
  - updated code to reduce DB query to 6 in 172.45ms. The number  of queries this API makes to the DB is independent of the number of user in the DB.
- List Posts for followed users API Endpoint - http://127.0.0.1:8000/imageshare/posts/followed
  - reference to previous code version (465.88 ms (14 queries including 11 similar and 7 duplicates) for 4 posts). The number of queries depend on the number of posts that are returned within the request.
  - updated code to improve this endpoint to only 5 queries in 180.30ms regardless of the amount of posts by followed users.
    - include prefect_related in query for Posts to get the likes counts without repetition.
    - Get the `ids` of users that the authenticated user follows and put them in a list including the `id` of the authenticated user. 
    Filter the Post queryset for posts where the `created_by` fields in the following list. 
    Optimize by prefetching and selecting related fields for `created_by` and `likes`
- List Posts for all users API Endpoint - http://127.0.0.1:8000/imageshare/posts
  - previous code had 12 queries including 9 similar and 7 duplicates and total run time 527.50 ms.
  - include `prefect_related` in query for Posts to get the `created_by` field for posts.
    - 161.80 ms (5 queries )
- Get a Post API Endpoint - http://127.0.0.1:8000/imageshare/posts/<post_id>
  - previous query ran in 174.72 ms (7 queries including 6 similar and 6 duplicates ) for a post with 3 likes.
  - include `prefect_related` in query for Posts to get the `created_by` and `likes` fields for posts.
    - 167.60 ms (4 queries ) independent of the number of likes on a post.
- 
### Don’t retrieve things you don’t need
- 

## Code Constraints
- Like model: Every `Like` object must be unique for the `liked_by` and `post` fields. This means that a post can only be liked once by a user.
  -  Add a `UniqueConstraint` constraint in the model's Meta class to ensure that each combination of `post` and `liked_by` is unique, meaning a user can only like a post once.
This will prevent duplicate likes and enforce the uniqueness at the database level.
- Follow model: Every `Follow` object must be unique for the `created_by` and `following` fields. This means that a user cannot follow another user twice. 
  - Add a `UniqueConstraint` constraint in the model's Meta class to ensure that each combination of `created_by` and `following` is unique.
This will enforce the uniqueness at the database level.
- User model: Every user must have a unique email address if they provide one.
  - Add a `UniqueConstraint` constraint in the model's Meta class to ensure that each User object cannot have duplicate email fields.
- Follow API - Put condition in the `perform_create` method for this api view to ensure that the authenticated user is unable to follow themselves.

## Authentication
using Simple JWT for DRF. Increase the token life span.

## Additional Features
- Pagination for `Posts` and `Users`  using `rest_framework` `PageNumberPagination`
- Basic search for posts by caption using `rest_framework` filters.

## Django Admin
- Add `list_filter` in the Follow admin view for the `created_by` and `following` fields to make it easy to view the followers of a specific user or to view the users that a specific user follows.
- Add `search_fields` and `list_filter` for Post admin view to enable an admin user to search for a post by its `caption` or `id` or filter posts by the `created_by` field.
- 