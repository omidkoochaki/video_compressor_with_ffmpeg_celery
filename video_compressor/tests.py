import time
from pathlib import Path

import ffmpeg
from redis import Redis
from django.test import TestCase

# Create your test_files here.
from vcom.video_compressor.models import Video
import subprocess


class ProcessTest(TestCase):
    def setUp(self) -> None:
        """
            make sure that test_video.mp4 file exists in vcom/test_files folder
        """
        self.video_file = 'test_files/test_video.mp4'

    def test_upload_video_file(self):
        video = Video(main_video=self.video_file)
        video.save()
        video_id = video.id
        time.sleep(10)
        print(Path("uploaded_videos/test_video.mp4").exists())
        saved_video = Video.objects.get(id=video_id)
        stream_240 = ffmpeg.probe(video.video_240)
        stream_240_video = next((stream for stream in stream_240['streams'] if stream['codec_type'] == 'video'), None)
        stream_360 = ffmpeg.probe(video.video_360)
        stream_360_video = next((stream for stream in stream_360['streams'] if stream['codec_type'] == 'video'), None)
        width_240 = int(stream_240_video['width'])
        width_360 = int(stream_360_video['width'])
        self.assertEqual(width_240, 240)
        self.assertEqual(width_360, 360)
        self.assertEqual(saved_video.main_video.name, "uploaded_videos/test_video.mp4")
        self.assertEqual(saved_video.video_240.name, "uploaded_videos/test_video_240.mp4")
        self.assertEqual(saved_video.video_360.name, "uploaded_videos/test_video_360.mp4")
        self.assertTrue(Path("uploaded_videos/test_video.mp4").exists())
        self.assertTrue(Path("uploaded_videos/test_video_240.mp4").exists())
        self.assertTrue(Path("uploaded_videos/test_video_360.mp4").exists())


def is_redis_available():
    r = Redis(host='localhost', port=6379)
    try:
        r.ping()
    except Exception as e:
        raise e
    return True


class IntegrationTests(TestCase):
    def test_integration_with_ffmpeg(self):
        subprocess.call(['ffmpeg', '-i', 'uploaded_videos/test_video.mp4',
                         '-filter:v', 'scale=', f'320 / 240 * iw: ih', 'uploaded_videos/test_video_320_240.mp4'])
        time.sleep(10)
        self.assertTrue(Path("uploaded_videos/test_video_320_240.mp4").exists())
        stream = ffmpeg.probe("uploaded_videos/test_video_320_240.mp4")
        stream_video = next((stream for stream in stream['streams'] if stream['codec_type'] == 'video'), None)
        width, height = int(stream_video['width']), int(stream_video['height'])
        self.assertEqual(width, 360)
        self.assertEqual(height, 240)

    def test_integration_with_redis(self):
        self.assertTrue(is_redis_available())
