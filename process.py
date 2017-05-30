import cv2
import threading
import time
import os

import cut_detector

class Process(object):
    def __init__(self, desc_cb, ws):
        self.ws = ws

        self.pipe_r_sd, self.pipe_w_sd = os.pipe()
        os.set_inheritable(self.pipe_w_sd, True)

        self.desc_cb = desc_cb

        self.processed = -1

        process = threading.Thread(target=self.process_loop)
        process.start()

    def process_loop(self):
        cap_sd = cv2.VideoCapture('pipe:%d' % self.pipe_r_sd)
        fps = cap_sd.get(cv2.CAP_PROP_FPS)

        print('pr: opened video')

        det = cut_detector.ContentDetector()
        orb = cv2.ORB_create()

        i = 0
        scene = 0

        while cap_sd.isOpened():
            ret, frame = cap_sd.read()
            print('pr: read frame', i)

            is_cut = det.process_frame(i, frame)

            kp = orb.detect(frame, None)

            kp, des = orb.compute(frame, kp)

            # img2 = cv2.drawKeypoints(frame, kp, None, color=(0,255,0), flags=0)
            # cv2.imshow('', img2)
            # cv2.waitKey(0)
            # 1/0

            # call to descriptor callback
            self.desc_cb(i, des, is_cut)

            if is_cut:
                print('pr: cut at', i)
                preview = 'frame%04d_%d.png' % (scene, i)
                cv2.imwrite(preview, frame)
                self.ws.sendJSON({
                    'scene': scene,
                    'time': frame2time(i, fps),
                    'preview': preview
                })
                scene += 1
            self.processed = i

            i += 1

        cap_sd.release()


def frame2time(fr, fps):
    s = fr / fps
    h = s // (60 * 60)
    m = (s // 60) % 60
    s = s % 60
    return "%d:%.2d:%06.3f" % (h, m, s)
