# Views

## CustomUserView

### def get_queryset(self):
Returns a queryset of CustomUser objects filtered by the currently authenticated user.
   **Returns:**
        - queryset of the current user.

### def get_object(self):
   **Returns:**   
        - The user that is currently authenticated.

### def destroy(self, request, *args, **kwargs):
Overridden method to prevent users from deleting their accounts.
This method returns a 405 Method Not Allowed response with a detail message indicating that deleting an account is not allowed.
    **Args:**
        - request: The HTTP request object.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.
    **Returns:**
        - Response: A DRF response object with a 405 Method Not Allowed status code and a detail explaining that deleting the account is not allowed.

### def me(self, request):
Return the user's profile or update the user's profile.
When the HTTP method is GET, this method returns the user's profile.
When the HTTP method is PUT or PATCH, this method updates the user's profile.
    **Args:**
        - request (Request): The request object.
    **Returns:**
        - Response: The response object that contains the user's profile or the updated user's profile.


## RegistrationView

### def post(self, request):
Creates a new user account and sends an activation email to the user.
Handle user registration by processing the request data with the RegistrationSerializer.
If the data is valid, create a new user, generate an activation token, and enqueue an email task to send an activation email to the new user.
    **Args:**
        - request: The request object.
    **Returns:**
        - A Response object with a 201 Created status code and a JSON object containing the user's id, email and a token to be used for activation.
        - If the request is invalid, returns a Response object with a 400 Bad Request status code and a JSON object containing the errors.


## ActivateUserView

### def get(self, request, uidb64=None, token=None):
GET endpoint to activate a user.
    - This endpoint is called after a user has registered and clicked on the activation link sent to their email.
    - The activation link contains a UID and token which are passed as parameters to this endpoint.
    - If the UID and token are valid, the user's account is activated.
    - If the UID and token are invalid, an error is returned.
    **Parameters:**
      - request:** The request object
      - uidb64: The base64 encoded user ID
      - token: The activation token 
    **Returns:**
      -  A DRF response object with a status code and a JSON object containing an error message if the activation fails.

### def post(self, request, uidb64=None, token=None ):
Activate a user account.
This method is called by the API endpoint to activate a user account.
It takes a uidb64 and a token as parameters, and calls the activate_user method.
If the uidb64 or token are not provided, it returns a 400 error response with an error message.
    **Parameters:**
        - request: The current request object.
        - uidb64 (str): The base64 encoded user id.
        - token (str): The password reset token.
    **Returns:**   
        - Response: response object with the result of the activation.

### def activate_user(self, uidb64, token):  
Activate a user's account given a valid base64 encoded user id and a valid password reset token.
    - Decodes the given uidb64 and retrieves the associated user instance from the database.
    - Checks that the given token is valid and not expired for the user.
    - If the token is valid, the user's account is activated and the user object is saved.
    - If the token is invalid or expired, return a 400 Bad Request with an appropriate error message.
    - If the user id is invalid or the user does not exist, return a 400 response with an appropriate error message.
    - If the user is successfully activated, return a 200 response with a success message.
    - If the user's account is already activated, returns a 200 OK response with a message.
    - If any other exception occurs, returns a 400 Bad Request response with an error message. 


## CookieTokenObtainPairView

### def post(self, request, *args, **kwargs): 
Handle a POST request to the CookieTokenObtainPairView endpoint.
The endpoint is similar to the TokenObtainPairView, but it also sets the access and refresh tokens as HttpOnly cookies.
The response body will contain the user's id and email, as well as a 'detail' message indicating the login was successful.
    **Parameters:**
        request: The current request object
    **Returns:**
            Response: A JSON response with the result of the login attempt
Set the access and refresh tokens as httponly cookies in the response.
    - The cookies are set with the "SameSite=Lax" attribute to prevent CSRF attacks.
    - The "secure" attribute is set to True in production to ensure the cookies are only sent over HTTPS.
    - The response data is updated to include a "detail" key with the message "Login successful", and a "user" key with the user's id and username.


## CookieTokenRefreshView

### def post(self, request, *args, **kwargs):
Overwrites the post method of TokenRefreshView to return a new access token in a HttpOnly cookie. The refresh token is obtained from the request cookies, and is validated before generating a new access token. If the refresh token is invalid or not found, an appropriate error response is returned.
    - If the refresh token cookie is not found, return a 400 Bad Request response with an appropriate error message.
    - If the refresh token is invalid, return a 401 Unauthorized response with an appropriate error message.
    - If the refresh token is valid, return a 200 OK response with the refreshed access token set as a HttpOnly cookie.


## LogoutView

### def post(self, request):
Handles user logout by blacklisting the refresh token and deleting authentication cookies.
This method attempts to retrieve the refresh token from the request's cookies.
    - If the refresh token is missing, it returns a 400 status code with an error message.
    - If the refresh token is invalid or expired, it returns a 400 status code with an error message.
    - Upon successful logout, it blacklists the refresh token, deletes the access and refresh token cookies, and returns a 200 status code with a success message.
    **Args:**
        - request: The HTTP request object containing cookies and other request data.
    **Returns:**
        - Response: DRF response object with an appropriate status code and message.


## CheckLoginOrRegisterView

### def post(self, request):
Check if a user should register or login based on the given email.
    - If the email does not exist, return a shouldRegister flag set to True.
    - If the email exists, return a shouldLogin flag set to True.
    **Args:**
        - request (Request): The HTTP request object.
    **Returns:**
        - Response: response object with a 200 status code and a JSON payload containing two boolean flags: shouldLogin and     shouldRegister.


## PasswordResetRequestView

### def post(self, request):
Handle a POST request to reset a user's password.
The request body should contain an 'email' key with the user's email address.
    - If the request is valid, sends an email to the user with a link to reset their password.
    - If the request is invalid, returns a 400 BAD REQUEST response with the serializer's errors.
    **Returns:**
      - 200 OK response with a detail message indicating that an email has been sent.
      - 400 BAD REQUEST response with the serializer's errors if the request is invalid.


## PasswordResetConfirmView

### def post(self, request, uidb64, token):
Resets the user's password given a valid base64 encoded user ID (uidb64) and a valid password reset token.
    - If the token is invalid or expired, it returns a 400 response with an appropriate error message.
    - If the user is successfully reset, it returns a 200 response with a success message.
    **Parameters:**
        - uidb64 (str): The base64 encoded user ID
        - token (str): The password reset token
    **Returns:**
        - Response: A DRF response object with a 200 status code and a detail message indicating that the password has been successfully reset, or a 400 status code with an appropriate error message.
  

## CategoryViewSet

### def create(self, request, *args, **kwargs):
Create a new category.
This action is only available to admins. It takes a JSON payload with the category's name and description. 
    - If the category is created successfully, it returns a 201 Created response with a JSON payload containing the category's name and description. 
    - If the category can't be created (for example, if the request is invalid or if the user is not an admin), it returns a 400 Bad Request or 403 Forbidden response with a JSON payload describing the error.
        **Parameters:**
            request (Request): The request object.
        **Returns:**
            Response: A JSON response with the result of the category creation. 

###  def categories_with_videos(self, request):
Return a list of categories, each containing a list of videos in that category
    **Parameters:**
        request (Request): The request object.    
    **Returns:**
        - A JSON response with the result of the category list with videos. A list of dictionaries, each with a 'category' key and a 'videos' key.
        The 'category' key maps to the name of the category, and the 'videos' key maps to a list of Video objects, each serialized as a dictionary.
    Example response:
        [
            {
                "category": "Comedy",
                "videos": [
                    {"id": 1, "title": "The Hangover", ...},
                    {"id": 2, "title": "Superbad", ...},
                    ...
                ]
            },
            {
                "category": "Drama",
                "videos": [
                    {"id": 3, "title": "The Shawshank Redemption", ...},
                    {"id": 4, "title": "The Godfather", ...},
                    ...
                ]
            },
            ...
        ]
        

## VideoViewSet

### def get_serializer_class(self):
Returns the serializer class to use based on the current action.
The VideoListSerializer is used for the list action, and the VideoSerializer is used for all other actions.
   **Returns:**
    - serializer class that should be used for the current action.

### def create(self, request, *args, **kwargs):        
Creates a new video.
    - The request should contain the title, description, duration, category ID, video file, and is_featured flag.
    - The response should contain the message 'Video created successfully' and the newly created video should exist in the database.
    **Parameters:**
        request (Request): The request object containing the video data.
    **Returns:**
        Response: A JSON response indicating the success or failure of the video creation process. 
            - If successful, returns a 201 status with a success message. 
            - If the input data is invalid, returns a 400 status with error details.

###  def new_video(self, request):
Retrieve the most recently created video.
The response will contain the video's title, description, duration, thumbnail URL, category and is_featured flag of the video.

### def new_videos(self, request):
Return a list of the 10 most recently created videos.
This endpoint returns a list of the 10 most recently created videos, ordered by creation date.
The response will contain a list of Video objects, with the following information:
    - id: The ID of the video.
    - title: The title of the video.
    - description: The description of the video.
    - duration: The duration of the video in minutes.
    - thumbnail_url: The URL of the video thumbnail.
    - category: The ID of the category of the video.
    - created_at: The creation date of the video.
    - user: The ID of the user who created the video.

### def featured(self, request):
Return a list of all videos that are featured.
The response will contain a list of the featured videos' titles, descriptions, durations, thumbnail URLs, category and is_featured flag of the video.


## def serve_hls_manifest(request, movie_id, resolution):
Returns the HLS manifest file for the given video and resolution.   
This endpoint requires authentication and returns the HLS manifest file for a video specified by the movie_id and resolution. The manifest file is served as a response with the content type 'application/vnd.apple.mpegurl'. 
    **Args:**
      - request: The request object.
      - movie_id: The ID of the video.
      - resolution: The resolution of the video (e.g. "1080p", "720p", "480p", etc.).
    **Returns:**
      - A FileResponse object containing the HLS manifest file.
    **Raises:**
      - Http404: If the video or manifest file does not exist.


## def serve_hls_segment(request, movie_id, resolution, segment):
Serves an HLS segment for a video.
    **Args:**
      - movie_id (int): The ID of the movie.
      - resolution (str): The resolution of the video.
      - segment (str): The name of the segment.
    **Returns:**
      - FileResponse: A response containing the segment file.
    **Raises:**
      - Http404: If the segment file does not exist.


## WatchlistViewSet

### def get_queryset(self): 
Returns a queryset of Watchlist objects for the authenticated user.
Filters the Watchlist objects to only include entries belonging to the currently authenticated user.
   **Returns**
    - A queryset of WatchlistEntry objects that belong to the authenticated user's watchlist.

### def perform_create(self, serializer): 
Create a new watchlist entry for the user.
    - If the watchlist entry already exists, raises a ValidationError.
    **Parameter:**
        - serializer: The serializer for the watchlist entry to be created.
    **Returns:**
        - None


##  WatchlistEntryViewSet

### def get_queryset(self):  
Returns a queryset of WatchlistEntry objects for the authenticated user.
Filters the WatchlistEntry objects to only include entries that belong to the authenticated user's watchlist.    
    **Returns:**
        QuerySet: A queryset of WatchlistEntry objects.

### def perform_create(self, serializer):   
Create a new watchlistEntry for the user.
Check:
    - If the video is already in the user's watchlist before saving the entry.
    - If the video is already in the watchlist, raise a ValidationError.
    - Otherwise, save the entry with the current user's watchlist.

### def remove_video(self, request, video_id=None):
Removes a video from the authenticated user's watchlist.
This action is triggered by a DELETE request to the 'remove/<video_id>' endpoint.
It checks if the user's watchlist exists and if the specified video is present in the watchlist.
- If the video is found, it is removed from the watchlist.
    **Args:**
      - request: The HTTP request object.
      - video_id: The ID of the video to be removed from the watchlist.
    **Returns:**
        A Response indicating the success or failure of the removal operation.
      - 204 No Content: Video was successfully removed from the watchlist.
      - 404 Not Found: Watchlist or video not found in the user's watchlist.


## WatchHistoryViewSet

### def get_queryset(self):  
   **Returns:**
     - queryset of WatchHistory objects filtered by the currently authenticated user.

### def perform_create(self, serializer):
Set the user attribute of the WatchHistory instance before saving it.
Because we are using a ModelViewSet, the create method is called automatically when a POST request is sent to the watch history endpoint. To ensure that the user attribute of the WatchHistory instance is set to the currently authenticated user, we override the perform_create method to call serializer.save() with the user parameter set to self.request.user.

This is necessary because the user field is read-only in the serializer, so it is not set by the deserialization of the request data.
    **Args:**
        - serializer: The watch history serializer to be used
    **Returns:**
        - A response with a 201 Created status code if the watch history entry is successfully created

### def save_progress(self, request):
Save the progress of a video for the current user.
    **Args:**
      - video_id: The id of the video
      - progress_seconds: The progress in seconds
    **Returns:**
      - The created WatchHistory object if it didn't exist, the updated WatchHistory if it did.
      -  A response with a 201 Created status code if the watch history entry is successfully created.
      -  A response with a 200 OK status code if the watch history entry is successfully updated
    **Raises:**
      - 400 Bad Request if the video_id or progress_seconds is missing or invalid
      - 404 Not Found if the video is not found """

### def get_progress(self, request, video_id=None):
Get the progress of a video for the current user.
This method retrieves the WatchHistory object for the given video_id and user and returns its progress_seconds value. If no such object exists, it returns a response with a progress_seconds value of 0.
    **Args:**
      - request: The HTTP request object.
      - video_id: The id of the video for which to retrieve the progress.
    **Returns:**
      - Response: A DRF response object with a progress_seconds value.
      - A response with a 200 OK status code containing the progress in seconds.
    **Raises:** 
            - Http404 if the video is not found