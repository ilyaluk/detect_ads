import cv2
import threading
import time
import os

import detector

class Segmenter(object):
    def __init__(self, cut_cb, save_path=None):
        self.pipe_r_hd, self.pipe_w_hd = os.pipe()
        os.set_inheritable(self.pipe_w_hd, True)

        self.pipe_r_sd, self.pipe_w_sd = os.pipe()
        os.set_inheritable(self.pipe_w_sd, True)

        self.cut_cb = cut_cb

        t = threading.Thread(target=self.loop)
        t.start()

    def loop(self):
        cap = cv2.VideoCapture('pipe:%d' % self.pipe_r_sd)
        det = detector.ContentDetector()
        i = 0

        while cap.isOpened():
            ret, frame = cap.read()
            is_cut = det.process_frame(i, frame)
            # if is_cut:
            self.cut_cb(i, is_cut)
            i += 1

        cap.release()
