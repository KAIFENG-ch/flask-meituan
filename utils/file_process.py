import os
import time

basedir = os.path.abspath(os.path.dirname(__file__)).rsplit('\\', 1)[0]
ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'}

video_file = {'mp4', 'MP4'}


def allowed_photo_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in video_file


def process(f, file_dir):
    f_name = f.filename
    ext = f_name.rsplit('.', 1)[1]
    unix_time = int(time.time())
    new_filename = str(unix_time) + '.' + ext
    new_path = os.path.join(file_dir, new_filename)
    f.save(new_path)
    return new_path


def photo_process(f, file_dir):
    if f and allowed_photo_file(f.filename):
        return process(f, file_dir)
    else:
        return None


def video_process(f, file_dir):
    if f and allowed_video_file(f.filename):
        return process(f, file_dir)
    else:
        return None
