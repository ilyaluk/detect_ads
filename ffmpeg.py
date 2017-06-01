import subprocess
import time
import os

class FFMpeg(object):
    def __init__(self, src, file_high, pipe_low):
        if os.path.isfile(file_high):
            os.remove(file_high)

        self.copy = subprocess.Popen(['ffmpeg', '-y', '-i', src,
                                      '-c', 'copy', '-bsf:v', 'h264_mp4toannexb', '-hls_list_size', '0', file_high],
                                     stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
                                     close_fds=False)

        while not os.path.isfile(file_high):
            time.sleep(1)

        comp = subprocess.Popen(['ffmpeg', '-y', '-live_start_index', '0', '-i', file_high,
                                 '-s', '320x180', '-f', 'mpegts', 'pipe:%d' % pipe_low],
                                stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
                                close_fds=False)

        print('ffmpeg: started \'em')

    def kill(self):
        self.copy.terminate()
