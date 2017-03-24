import threading
import time
import os
import subprocess

class STIP(object):
    def __init__(self, callback):
        self.callback = callback

        stip_fifo = 'stip_fifo.ts'
        if os.path.exists(stip_fifo):
            os.remove(stip_fifo)
        os.mkfifo(stip_fifo)
        self.fifo = stip_fifo

        stip_list = 'stip_list.txt'
        open(stip_list, 'w').write(stip_fifo[:stip_fifo.rindex('.')] + '\n')

        # patch STIP: 0x0001a57a 488b => eb3a
        # and hopefully you have
        # libcvaux.so.2  libcv.so.2  libcxcore.so.2  libhighgui.so.2  libml.so.2
        # in your ld path or in ./stip-2.0-linux/lib/
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = os.getcwd() + '/stip-2.0-linux/lib'

        self.proc = subprocess.Popen([
          './stip-2.0-linux/bin/stipdet', '-i', stip_list, '-ext', '.' + stip_fifo.split('.')[-1],
          '-vpath', './', '-stdout', 'yes', '-o', '/dev/null', '-vis', 'no'#, '-thresh', '0.000015',
          ], stdout=subprocess.PIPE, env=env)


        t = threading.Thread(target=self.stip_loop)
        t.start()

    def stip_loop(self):
        debounce = {}
        threshold = 10

        while 1:
            # point-type y-norm x-norm t-norm y x t sigma2 tau2 dscr-hog(72) dscr-hof(90)
            tmp = [b'#']
            while tmp[0].startswith(b'#') or tmp == [b'']:
                tmp = self.proc.stdout.readline().split(b' ')
            point_type = int(tmp[0])
            y_norm = float(tmp[1])
            x_norm = float(tmp[2])
            y = int(tmp[4])
            x = int(tmp[5])
            t = int(tmp[6])
            sigma2 = float(tmp[7])
            tau2 = float(tmp[8])
            hog = tuple(map(float, tmp[9:9+72]))
            hof = tuple(map(float, tmp[9+72:9+72+90]))

            # print('STIP', t)

            if t in debounce:
                debounce[t] += ((x, y) + hog + hof),
            elif len(debounce) == 0 or t > max(debounce):
                debounce[t] = ((x, y) + hog + hof),

            while len(debounce) > threshold:
                tmp = min(debounce)
                self.callback(t, debounce[tmp])
                del debounce[tmp]
