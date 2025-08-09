# Videoflix Backend API

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/HTK-MM/Videoflix_backend/blob/master/README.MD) [![de](https://img.shields.io/badge/lang-de-yellow.svg)](https://github.com/HTK-MM/Videoflix_backend/blob/master/README.de.md)

## Description

Videoflix Backend is an API of a video streaming app, built with Django and Django REST Framework. It provides APIs for user accounts, video upload, categories, watchlists, and more.

## Main Features

- User registration, login, and password reset  
- JWT authentication using HTTP-only cookies  
- Upload videos and generate thumbnails automatically  
- Convert videos to different resolutions with Celery and FFmpeg  
- Generate HLS streams for smooth playback  
- Create and list video categories  
- Save videos to a personal watchlist  
- Track watch history for each user  
- Runs with Docker and PostgreSQL  

## Technologies Used

- **Python 3.x** – Programming language
- **Django 5.2.3** – Web framework
- **Django REST Framework 3.16.0** – API development
- **SimpleJWT** – JWT-based authentication with cookies
- **Redis + django-rq** – Background tasks with job queues
- **FFmpeg + ffmpeg-python** – Video processing
- **PostgreSQL** – Production database
- **Gunicorn** – WSGI server for deployment
- **Whitenoise** – Serve static files in production
- **Docker** – Containerization and environment management

## Documentation

The complete project documentation is located in the [`docs/`](./docs/) folder, in Markdown (`.md`) format.  
This documentation has been generated from the **docstrings** included in the source code, so it contains a description of each function, its parameters, and its purpose within the project.  
It is especially useful for developers who want to understand the internal workings of the code and have a precise reference of what each part of the application does.

**Example:**
    ```python
    def video_post_save(sender, instance, created, **kwargs):
        """
        Signal receiver that is called after a Video instance is saved.
        If the Video instance is newly created, it performs tasks such as:
        - Converting the video file to different resolutions.
        - Generating a thumbnail.
        - Creating HLS streams.
        """
    ```


## Installation

This project uses Docker. Follow these steps to get everything running locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/HTK-MM/Videoflix_backend/.git
   cd Videoflix_backend
   ```

   
2. The project requires several environment variables to be set for proper configuration. An example file `.env.template` is included in the repository with all the necessary keys and placeholder values.
   To set up your environment variables, create a `.env` file based on the template and configure it with your own values:
    ````bash   
    cp .env.template .env
    # Then edit the .env file with your actual configuration values (database CREDENTIALS, SECRET_KEY, DATABASE_URL, EMAIL_* settings, etc.)
    ````

3. Start the containers:
    ````bash   
    docker-compose up --build
    ````

4. Access the API at: http://localhost:8000
   
5. Create a superuser inside the container (only once):
   ````bash   
    docker-compose exec web python manage.py createsuperuser
    ```` 

6. Configure the database and apply migrations:
    ````bash 
    docker-compose exec web python manage.py migrate
    ````

7.  Stopt the containers:
    ````bash   
    docker-compose down
    ````
## Admin Panel Access 

Only users with `is_staff=True` can access the Django admin panel.  
Superusers (`is_superuser=True`) have full access.  
Models such as `Watchlist`, `WatchlistEntry`, and `WatchHistory` are only visible to superusers to protect user privacy.

## API Base Path

All API endpoints are prefixed with `/api/`.  
Example:  
- `GET /api/video/` – Returns a list of all videos.
- `POST /api/login/` – Authenticates a user and returns a JWT.

The full Django `urlpatterns` configuration includes:

    ```python
urlpatterns = [
    path('admin/', admin.site.urls),                  # Admin interface
    path('api/', include('videoflix_app.api.urls')),  # Main API
    path('django-rq/', include('django_rq.urls')),    # Task queue monitoring
]
    ```

## API Endpoints

The Videoflix API provides the following endpoints:

### :small_blue_diamond: Authentication & Users

-   ````**POST /register/**```` - Register a new user. 
-   ````**GET /activate/<uidb64>/<token>/**```` - Account activation via token (email).
-   ````**POST /login/**```` -  Log in with JWT (stored in cookie).
-   ````**POST /token/refresh/**```` -  Refresh the JWT token. 
-   ````**POST /logout/**```` -  Log out and clear authentication cookies. 
-   ````**GET /users/check-login-register/**```` - Check if the user needs to register or log in.
-   ````**POST /password_reset/**```` -  Request a password reset via email.
-   ````**POST /password_confirm/<uidb64>/<token>/**```` -  Confirm password reset. 
-   ````**`GET` | `PUT` | `DELETE` /user/**```` -  Manage the authenticated user profile.
  
### :small_blue_diamond: Categories
-   ````**GET /categories/**```` - List all available video categories. 
-   ````**POST /categories/**```` - Create a new category.   

### :small_blue_diamond: Videos

-   ````**GET /video/**```` - Retrieve a list of all videos. 
-   ````**GET /video/<id>/**```` - Get details of a specific video.
-   ````**GET /video/<movie_id>/<resolution>/index.m3u8**```` - Get the HLS manifest for the video.
-   ````**GET /video/<movie_id>/<resolution>/<segment>/**```` - Get a specific HLS video segment.

### :small_blue_diamond: Watchlist

-   ````**`GET` | `POST` /watchlist/**```` - Access or modify the user's watchlist.
-   ````**`GET` | `DELETE` /watchlist-entries/**```` - Manage individual entries in the watchlist.





## Testing

### Running tests with Docker
1. Make sure your containers are running:
    ````bash   
    docker-compose up 
    ````    
2. Apply migrations inside the container (only needed if not done yet):
   ````bash   
    docker-compose exec web python manage.py migrate
    ````    
3. To run test inside the Docker container, use:
    ````bash   
    docker-compose exec web python manage.py test
    ````    
4. When finished, you can stop the containers:
    ````bash   
    docker-compose down
    ````   

