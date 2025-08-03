# Serializers

## CustomUserSerializer

### def update(self, instance, validated_data):
Updates an existing CustomUser instance with the given validated data.
This serializer's update method is called by the ModelViewSet's update method.
The update method of ModelViewSet gets the instance to be updated from the queryset, and then calls this serializer's update method to update the instance.
The validated data is passed as argument to this method.
This method iterates over the validated data, sets the attributes of the instance with the corresponding values, saves the instance and returns it.


## MyTokenObtainPairSerializer

### def __init__(self, *args, **kwargs):
    - Removes username from the validated data since we are using email
    - instead.
  
### def validate(self, attrs):  
Validates the user credentials and populates the validated_data dictionary.
        
        Validations:
        - checks if user is registered
        - checks if the password is correct
        - checks if the user is active
        - populates the validated_data dictionary with the user's username, email and id
        
        If any validation fails, raises serializers.ValidationError


## RegistrationSerializer

### def validate_password(self, value):
Check that the password is at least 8 characters long.
    **Args**: 
      - value: The password to check.
    **Raises**:
      - serializers.ValidationError: If the password is less than 8 characters long.

### def validate_email(self, value):
Checks if email already exists in database.
If it does, raises serializers.ValidationError with message 'Email already exists'.
Otherwise, returns the email.

### def validate(self, data):    
Validate the given data.
Checks that the given password and confirmed password match, and raises a ValidationError if they do not.

### def create(self, validated_data): 
Creates a new user with the given email and password.
    -   The username is set to the part of the email before the '@' symbol.
    -   The user is created with the 'is_active' field set to False, meaning they are in an inactive state
        and cannot log in until they are activated.
    **Returns:**
        - the newly created user instance


## PasswordResetRequestSerializer

### def validate_email(self, value):  
Validate the email address passed in the request. If the email address is not valid according to Django's email validation, raises a ValidationError.


## PasswordResetConfirmSerializer

### def validate(self, data): 
Validates the data for a password reset confirmation.

-   Validates that the token and uid are present in the context. Checks that the new password and repeat password match.
-   Decodes the uidb64 and checks that the user exists. Then checks that the token is valid for the given user.
-   If everything is valid, adds the user to the validated data and returns it.
    **Raises:**
        - serializers.ValidationError if any of the checks fail.
  
### def save(self):
Save the new password for the user.
This method sets the new password for the user instance obtained from the validated data and saves the user object with the updated password.


## VideoSerializer

### def get_video_base_url(self, obj): 
Retrieve the base URL of the video file associated with the given object.
If the video file URL ends with '.mp4', return the URL without the file extension.
Otherwise, return the full URL.
    **Args:**
        - obj: The Video instance containing the video file.
    **Returns:**
        - str or None: The base URL of the video file, or None if no video file is present.

### def get_thumbnail_url(self, obj): 
Return the absolute url of the video thumbnail image.
If the object doesn't have a thumbnail, return None


## VideoListSerializer

### def get_thumbnail_url(self, obj):
Retrieve the absolute URL of the thumbnail for the given video object.
    **Args:**
        - obj (Video): The video object for which to retrieve the thumbnail URL.
    **Returns:**
        - str or None: The absolute URL of the thumbnail if available, otherwise None.