# Signals

### def video_post_save(sender, instance, created, **kwargs):
Signal receiver that is called after a Video instance is saved.
If the Video instance is newly created, it performs the following tasks:
    - Enqueues a task to convert the video file to different resolutions.
    - Enqueues a task to generate a thumbnail from the video file.
    - Enqueues a task to generate an HLS stream for each resolution.    
    **Parameters:**
      - sender (Video): The model class that sent the signal.
      - instance (Video): The Video instance that was saved.
      - created (bool): Indicates whether the instance was created (True) or updated (False).

### def video_post_delete(sender, instance, **kwargs):
Handle post-delete signals for Video instances.
This function is triggered after a Video instance is deleted. It performs cleanup by removing associated video files, thumbnail images, and HLS folders from the file system.
    **Args:**
      - sender: The model class that sent the signal.
      - instance: The actual instance being deleted.
      - **kwargs: Additional keyword arguments.
