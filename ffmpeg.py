import subprocess

class FFMpeg(object):
    def __init__(self, src, pipe_high, pipe_low, fifo):
        # TODO: no fiter and -c copy for pipe_high
        proc = subprocess.Popen(['ffmpeg', '-y', '-i', src,
            '-filter_complex',
            '[0:v]split=2[in2][in3];[in2]null[out2];[in3]format=gray[out3]',
            '-map', '[out2]', '-s', '160x90', '-f', 'mpegts', 'pipe:%d' % pipe_low,
            '-map', '[out3]', '-s', '160x90', '-r', '5', fifo,
            ],
            stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
            close_fds=False)
        # proc = subprocess.Popen(['ffmpeg', '-y', '-i', src,
        #     '-filter_complex',
        #     '[0:v]split=3[in1][in2][in3];[in1]null[out1];[in2]null[out2];[in3]format=gray[out3]',
        #     '-map', '[out1]', '-f', 'mpegts', 'pipe:%d' % pipe_high,
        #     '-map', '[out2]', '-s', '160x90', '-f', 'mpegts', 'pipe:%d' % pipe_low,
        #     '-map', '[out3]', '-s', '160x90', '-r', '5', fifo,
        #     ],
        #     stdin=None, stdout=None, stderr=None,
        #     close_fds=False)
