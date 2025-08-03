from .models import Video
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from .api.tasks import convert_resolution, generate_and_save_thumbnail_task, generate_hls
import os, django_rq, shutil


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):       
    if created:
        if not instance.video_file:            
            return       
        queue = django_rq.get_queue('default', autocommit=True)
        widths = [120, 360, 480, 720, 1080]
        for width in widths:
            queue.enqueue(convert_resolution, instance.video_file.path, width)
        queue.enqueue(generate_and_save_thumbnail_task, instance.id)
        video_path = os.path.join(settings.MEDIA_ROOT, 'videos', os.path.basename(instance.video_file.name))        
        hls_output_folder = os.path.join(settings.MEDIA_ROOT, 'videos', str(instance.id))
        for res in widths:
            output_folder = os.path.join(hls_output_folder, f'{res}p')
            queue.enqueue(generate_hls, video_path, output_folder, str(res))
        

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
       if os.path.isfile(instance.video_file.path):
           os.remove(instance.video_file.path)
           print('Video is deleted')    
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)
        print(f"Thumbnail deleted: {instance.thumbnail.path}")        
    hls_folder = os.path.join(settings.MEDIA_ROOT, 'videos', str(instance.id))
    if os.path.isdir(hls_folder):
        shutil.rmtree(hls_folder)
        print(f"HLS folder deleted: {hls_folder}")