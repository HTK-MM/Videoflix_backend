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
Initialize the MyTokenObtainPairSerializer instance. This constructor overrides the parent constructor to remove the 'username' field from the serializer's fields, as email is used for authentication instead.
- Removes username from the validated data since we are using email
- instead.
    **Args:**
        *args: Variable length argument list to pass to the parent class.
        **kwargs: Arbitrary keyword arguments to pass to the parent class.
  
### def validate(self, attrs):  
Validates the given attributes (email and password).
- If the email is not registered, raises a ValidationError with message 'Email address is not registered'.
- If the email and password do not match, raises a ValidationError with message 'Invalid emailaddress or password'. 
- If the user is not active, raises a ValidationError with message 'User is not active'. 
- Otherwise, sets the 'username' attribute of the validated data to the username of the user, and returns the validated data.
Also, adds the 'user_id' and 'email' to the validated data, which are the id and email of the user, respectively.        
    **Validations:**
        - checks if user is registered
        - checks if the password is correct
        - checks if the user is active
        - populates the validated_data dictionary with the user's username, email and id.
        
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
Validates the given data by checking if the given password and confirmed password match.
If they do not match, raises a serializers.ValidationError with a message indicating that the passwords do not match.
Otherwise, returns the validated data.


### def create(self, validated_data): 
Creates a new user with the given email and password.
This serializer's create method is called by the ModelViewSet's create method.
The validated data is passed as argument to this method.
    -   The email address is used to create a username (by stripping the domain part).
    -   The username is set to the part of the email before the '@' symbol.
    -   The user is created with the username and email address. The password is set to the given password.
    -   The user is created with the 'is_active' field set to False, meaning they are in an inactive state
        and cannot log in until they are activated.
    **Returns:**
        - the newly created user instance


## PasswordResetRequestSerializer

### def validate_email(self, value):  
Validate the email address passed in the request. If the email address is not valid according to Django's email validation, raises a ValidationError. ValidationError with the message 'Email already exists'.
Otherwise, returns the email value.


## PasswordResetConfirmSerializer

### def validate(self, data): 
Validates the data for a password reset confirmation.
Validates the given data by performing the following checks:
    1. Checks that the 'uidb64' and 'token' are present in the context.
    2. Checks that the given new password and confirmed password match.
    3. Decodes the uidb64 and checks that the user exists. Then checks that the token is valid for the given user.
    4. Attempts to decode the 'uidb64' and retrieve the user instance from the database.
    5. Checks that the token is valid and not expired.
    6. If any of the checks fail, raises a serializers.ValidationError with an appropriate error message.
    7. If all the checks succeed, returns the validated data with the user instance included.
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
Returns the absolute URL of the video's thumbnail.  
If the video instance has an associated thumbnail and a request context is provided, 
constructs and returns the full URL to access the thumbnail image. If no thumbnail 
exists or no request context is available, returns None.    
    **Args:**
        obj: The video instance containing the thumbnail information.    
    **Returns:**
        str or None: The absolute URL of the thumbnail image or None if unavailable.


## VideoListSerializer

### def get_thumbnail_url(self, obj):
Retrieve the absolute URL of the thumbnail for the given video object.
This method calls the `get_thumbnail_url` method from `VideoSerializer` to obtain the URL. The method requires an object to be passed as an argument.
    **Args:**
        - obj (Video): The video object for which to retrieve the thumbnail URL.
    **Returns:**
        - str or None: The absolute URL of the thumbnail if available, otherwise None.