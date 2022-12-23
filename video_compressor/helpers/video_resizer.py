import os
import warnings

import ffmpeg


def video_resizer(video_path, output_path, width, overwrite=False):
    '''
    use ffmpeg to resize the input video to the width given, keeping aspect ratio
    '''
    if not (os.path.isdir(os.path.dirname(output_path))):
        raise ValueError(f'output_path directory does not exists: {os.path.dirname(output_path)}')

    if os.path.isfile(output_path) and not overwrite:
        warnings.warn(f'{output_path} already exists but overwrite switch is False, nothing done.')
        return None

    input_vid = ffmpeg.input(video_path)
    vid = (
        input_vid
        .filter('scale', width, -1)
        .output(output_path)
        .overwrite_output()
        .run()
    )
    return output_path
