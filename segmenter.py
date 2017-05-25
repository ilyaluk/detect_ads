import cv2
import threading
import time
import os
import subprocess
import tempfile

import detector

class Segmenter(object):
    def __init__(self, desc_cb):
        self.pipe_r_sd, self.pipe_w_sd = os.pipe()
        os.set_inheritable(self.pipe_w_sd, True)

        self.desc_cb = desc_cb

        self.processed = -1

        detect = threading.Thread(target=self.detect_loop)
        detect.start()

    def detect_loop(self):
        cap_sd = cv2.VideoCapture('pipe:%d' % self.pipe_r_sd)
        print('Opened SD')

        # TODO: move this loop to detector
        det = detector.ContentDetector()
        i = 0
        scene = 0
        while cap_sd.isOpened():
            ret, frame = cap_sd.read()
            is_cut = det.process_frame(i, frame)

            # call to descriptor callback
            self.desc_cb(i, is_cut)

            if is_cut:
                print('Cut at', i)
                cv2.imwrite('frame%04d_%d.png' % (scene, i), frame)
                scene += 1
            self.processed = i

            i += 1

        cap_sd.release()
