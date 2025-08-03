from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from email.mime.image import MIMEImage
import os
import subprocess
import ffmpeg
from django.core.files import File
from videoflix_app.models import Video

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

def build_activation_email_content(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
    context = {'mail': user.username, 'activation_link': link}
    return get_template('email.html').render(context)

def attach_cid_image(email, image_path, cid_name):
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            image = MIMEImage(img.read(), _subtype='png')
            image.add_header('Content-ID', f'<{cid_name}>')
            image.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            email.attach(image)          
    else:
        print("Image not found at:", image_path)

def send_activation_email_task(user_id):
    user =   User.objects.get(pk=user_id)
    content = build_activation_email_content(user)
    email = EmailMultiAlternatives(
        subject='Confirm your email',
        body='Registration',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]) 
    email.fail_silently = False
    email.attach_alternative(content, 'text/html')    
    image_path = os.path.join(settings.BASE_DIR, 'videoflix_app','templates', 'Logo.png')
    attach_cid_image(email, image_path,'logo_videoflix')    
    email.send()

def send_resetPW_email_task(user_id):
    user = User.objects.get(pk=user_id)
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
    context = {'mail': user.username, 'resetPW_link': link}
    content = get_template('resetPW_email.html').render(context)
    email_obj = EmailMultiAlternatives(
        'Password Reset: Reset your Password',
        'Password Reset body',
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email_obj.attach_alternative(content, 'text/html')
    image_path = os.path.join(settings.BASE_DIR, 'videoflix_app','templates', 'Logo.png')    
    attach_cid_image(email_obj, image_path, 'logo_videoflix')
    email_obj.send()

def generate_thumbnail(video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        print(f"Video with id={video_id} does not exist")
        return None
    if not video.video_file:
        print(f"Video with id={video_id} has no video file")
        return None
    video_path = video.video_file.path
    filename_base = os.path.splitext(os.path.basename(video_path))[0]
    thumbnail_path = os.path.join(os.path.dirname(video_path), f'{filename_base}_thumb.jpg')
    try:
        (ffmpeg
        .input(video_path, ss='00:00:01')
        .output(thumbnail_path, vframes=1)
        .run()   )
        print(f"Thumbnail generated for video {video.id} at {thumbnail_path}")
        return thumbnail_path
    except Exception as e:
        print(f"Failed to generate thumbnail for video {video.id}: {e}")
        return None
    
def generate_and_save_thumbnail_task(video_id):
    video = Video.objects.get(id=video_id)
    thumbnail_path = generate_thumbnail(video_id)
    if thumbnail_path:
        save_thumbnail_to_video(video, thumbnail_path)

def save_thumbnail_to_video(instance, thumbnail_path):
    with open(thumbnail_path, 'rb') as f:
        instance.thumbnail.save(os.path.basename(thumbnail_path), File(f), save=True)
        
def convert_resolution(source, width):
    target = source.replace('.mp4', f'_{width}p.mp4')
    cmd = 'ffmpeg -i {} -vf "scale={}:-1" -c:v libx264 -crf 23 -c:a copy {}'.format(source, width, target)
    subprocess.run(cmd)

def get_video_duration(video_path):   
    result = subprocess.run(
        [   'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return float(result.stdout.strip())

def get_resolution_size(resolution):
    if resolution == "480":
        return 854, 480
    elif resolution == "720":
        return 1280, 720
    elif resolution == "1080":
        return 1920, 1080
    else:
        return 640, 360

def generate_hls(video_path, output_folder, resolution="480"):
    os.makedirs(output_folder, exist_ok=True)
    width, height = get_resolution_size(resolution)  
    duration = get_video_duration(video_path)
    hls_time = 2 if duration <= 10 else 10  
    output_path = os.path.join(output_folder, 'index.m3u8')
    try:
        (ffmpeg
            .input(video_path)            
            .output(
                output_path,
                vf=f'scale={width}:{height}',
                format='hls',
                hls_time=hls_time,
                hls_playlist_type='vod',
                hls_segment_filename=os.path.join(output_folder, 'segment_%03d.ts'),
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='128k',
                preset='fast',
                crf=20            
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)    )
        print("HLS generado con audio correctamente.")
    except ffmpeg.Error as e:
        print(f"Error generando HLS: {e.stderr.decode()}")
    return output_path