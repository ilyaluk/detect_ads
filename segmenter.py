import cv2
import threading
import time
import os

import detector

class Segmenter(object):
    def __init__(self):
        self.pipe_r_hd, self.pipe_w_hd = os.pipe()
        os.set_inheritable(self.pipe_w_hd, True)

        self.pipe_r_sd, self.pipe_w_sd = os.pipe()
        os.set_inheritable(self.pipe_w_sd, True)

        # t1 = threading.Thread(target=self.loop1)
        t = threading.Thread(target=self.loop)
        # t1.start()
        t.start()

    # def loop1(self):
    #     t = os.fdopen(self.pipe_r_hd, 'rb')
    #     reader = mpegts.TSRead(tsfd=t)
    #     for i in reader:
    #         print(i)

    def loop(self):
        cap = cv2.VideoCapture('pipe:%d' % self.pipe_r_sd)
        det = detector.ContentDetector()
        i = 0

        while cap.isOpened():
            ret, frame = cap.read()
            is_cut = det.process_frame(i, frame)
            if is_cut:
                print('CUT', i)
            i += 1

        cap.release()