import subprocess

class FFMpeg(object):
    def __init__(self, src, file_high, pipe_low, fifo):
        # TODO: no fiter and -c copy for pipe_high
        proc = subprocess.Popen(['ffmpeg', '-y', '-i', src,
                                 '-filter_complex',
                                 '[0:v]split=3[in1][in2][in3];[in1]null[out1];[in2]null[out2];[in3]format=gray[out3]',
                                 '-map', '[out1]', file_high,
                                 '-map', '[out2]', '-s', '160x90', '-f', 'mpegts', 'pipe:%d' % pipe_low,
                                 '-map', '[out3]', '-s', '128x72', fifo],
                                # TODO: lower fps for stip
                                stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
                                close_fds=False)