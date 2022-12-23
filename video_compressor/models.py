import ffmpeg
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db import transaction


# Create your models here.
from .helpers.video_resizer import video_resizer


class Video(models.Model):
    main_video = models.FileField(upload_to='uploaded_videos',
                                  validators=[FileExtensionValidator(
                                      allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]
                                  )
    video_240 = models.FileField(upload_to='uploaded_videos', null=True, blank=True,
                                 validators=[FileExtensionValidator(
                                     allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]
                                 )
    video_360 = models.FileField(upload_to='uploaded_videos', null=True, blank=True,
                                 validators=[FileExtensionValidator(
                                     allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]
                                 )
    compress_duration = models.PositiveIntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not update_fields:
            from .tasks.celery import video_compressor
            super().save(force_insert, force_update, using, update_fields)
            transaction.on_commit(lambda: video_compressor.delay(self.main_video.name, self.id))
        else:
            super().save(force_insert, force_update, using, update_fields)




