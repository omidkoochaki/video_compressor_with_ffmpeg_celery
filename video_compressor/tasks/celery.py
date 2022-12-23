import datetime
import os
from math import floor

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vcom.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def video_compressor(self, main_video_name, video_id):
    start_task = datetime.datetime.now().timestamp()
    from ..helpers.video_resizer import video_resizer
    from ..models import Video
    v360 = video_resizer(main_video_name, main_video_name.replace('.', '_360.'), 360, True)
    v240 = video_resizer(main_video_name, main_video_name.replace('.', '_240.'), 240, True)
    video = Video.objects.get(id=video_id)
    video.video_360 = v360
    video.video_240 = v240
    end_task = datetime.datetime.now().timestamp()
    video.compress_duration = floor(end_task - start_task)
    video.save(update_fields=['video_360', 'video_240', 'compress_duration'])
