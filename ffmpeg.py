import subprocess
import time

class FFMpeg(object):
    def __init__(self, src, file_high, pipe_low):
        copy = subprocess.Popen(['ffmpeg', '-y', '-i', src,
                                 '-c', 'copy', '-hls_list_size', '0', file_high],
                                stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
                                close_fds=False)
        time.sleep(3) # slould be enough for one chunk to be written
        comp = subprocess.Popen(['ffmpeg', '-y', '-live_start_index', '0', '-i', file_high,
                                 '-s', '160x90', '-f', 'mpegts', 'pipe:%d' % pipe_low],
                                stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
                                close_fds=False)
