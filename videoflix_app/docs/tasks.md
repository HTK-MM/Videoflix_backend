# Tasks

### def build_activation_email_content(user):
Builds the content for the activation email to be sent to the user. This function generates a base64 encoded UID and a token for the user, constructs an activation link using these values, and then uses a template to render the HTML email content with the user's username and activation link.
    **Args:**
        - user: The user to generate the email for.
    **Returns:**
        - A rendered HTML email template as a string.
  

### def attach_cid_image(email, image_path, cid_name):
Attaches an image to an email with a given cid_name. The image is read from the given image_path.
If the image does not exist at the given image_path, a message is printed to the console.
    **Args:**
        - email (EmailMultiAlternatives): The email object to attach the image to.
        - image_path (str): The file path to the image to be attached.
        - cid_name (str): The CID name to be used for the image in the email.
    **Raises:**
        - FileNotFoundError: If the image file does not exist at the given path.
        - 
This function opens the image file in binary mode, creates a MIMEImage object, and attaches it to the email with the specified CID. If the image file is not found at the specified path, it prints an error message.


### def send_activation_email_task(user_id):
Sends an activation email to the user with the given user_id.
    **Args:**
        - user_id (int): The id of the user to send the email to.
    **Returns:**
        - None


### def send_resetPW_email_task(user_id):
Sends a password reset email to the user with the given ID.
This function generates a password reset token and a unique link containing the user's base64 encoded id and the token. It then renders the reset password     email 'resetPW_email.html' template with the user's details and sends the email. An inline image is attached to the email as a Content-ID (CID).
    **Args:**
        - user_id (int): The ID of the user requesting a password reset.
    **Raises:**
        - User.DoesNotExist: If no user with the given ID is found.


### def generate_thumbnail(video_id):
Generate a thumbnail for a video at the given id.
Retrieves the video file associated with the given video_id, extracts the first frame of the video using ffmpeg, and saves it as a JPEG image in the same directory as the video file. If the video does not exist or has no video file, the function will not proceed with thumbnail generation.
    **Parameter:**
        - video_id: The id of the video for which to generate a thumbnail
    **Returns:**
        - str or None: The path to the generated thumbnail file, or None if generation failed.
   

### def generate_and_save_thumbnail_task(video_id):
Generates a thumbnail for the specified video and saves it to the Video instance.
    **Args:**
        - video_id (int): The ID of the video for which to generate and save the thumbnail.
This function retrieves the Video instance by its ID, generates a thumbnail by extracting a frame from the video file, and if successful, saves the generated thumbnail to the Video instance. If the video does not exist or has no video file, the function will not proceed with thumbnail generation.


### def save_thumbnail_to_video(instance, thumbnail_path):
Save a generated thumbnail image to a video instance.
    **Args:**
        - instance (Video): The video instance to which the thumbnail will be saved.
        - thumbnail_path (str): The file path of the thumbnail image to be saved.
The function opens the thumbnail image from the specified path in binary mode and saves it to the 'thumbnail' field of the video instance using Django's File API.

### def convert_resolution(source, width):
Convert a video file to a lower resolution.    
Takes a file path to a video file and a target width in pixels, and saves a converted version of the video to the same directory with "_{width}p" appended to the filename.
   
The conversion is done using ffmpeg, with the following options:    
    - Input: the source video file
    - Video filter: scale the video to the target width, keeping the aspect ratio
    - Video codec: libx264
    - Constant rate factor: 23
    - Audio codec: copy the audio from the source file (no re-encoding)
    **Args:**
        - source (str): The path to the source video file.
        - width (int): The target width for scaling the video.

### def get_video_duration(video_path):
Calculate and return the duration of a video file in seconds.
This function utilizes `ffprobe` to extract the duration metadata from the given video file path.
    **Parameters:**    
      - video_path (str):  Path to the video file.    
    **Returns:**    
      - float : The duration of the video in seconds.


### def get_resolution_size(resolution):
Return the resolution size (width, height) given the resolution string
    **Args:**
        resolution (str): "480", "720", "1080" or empty string
    **Returns:**
        tuple: A tuple containing the width and height corresponding to the resolution.



### def generate_hls(video_path, output_folder, resolution="480"):
Generate an HLS video from a given video file.
    **Parameters:**
        - video_path (str): Path to the video file to convert.
        - output_folder (str): Path to the folder to store the generated HLS segments.
        - resolution (str): Target resolution for the video. Supported values are '480', '720', '1080'.
    **Returns:**
        - str: Path to the generated HLS manifest file.
    **Raises:**
        - ffmpeg.Error: If the conversion fails.