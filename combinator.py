# import cv2
import numpy as np
import time

class Combinator(object):
    def __init__(self):
        self.window = 15 # frames

        self.cuts = set()
        self.start_descs = dict()
        self.end_descs = dict()
        self.cache = dict()
        self.processed = -1

    def cut_callback(self, t, is_cut):
        self.processed = t
        if is_cut:
            self.cuts.add(t)

    def frame_callback(self, t, descr):
        while t + self.window + 1 > self.processed:
            time.sleep(0.1)

        self.cache[t] = descr

        if min(self.cuts) <= t - self.window + 1:
            cur_cut = min(self.cuts)
            print(frame2time(cur_cut, 24))
            self.cuts.remove(cur_cut)

            tmp = np.array([])
            for i in range(0, self.window):
                if cur_cut + i in self.cache:
                    tmp = np.hstack((tmp, self.cache[cur_cut + i]))
                else:
                    tmp = np.hstack((tmp, np.zeros(len(descr))))
            self.start_descs[cur_cut] = tmp
            print(tmp)

            tmp = np.array([])
            for i in range(-self.window, 0):
                if cur_cut + i in self.cache:
                    tmp = np.hstack((tmp, self.cache[cur_cut + i]))
                else:
                    tmp = np.hstack((tmp, np.zeros(len(descr))))
            self.end_descs[cur_cut] = tmp
            print(tmp)

            self.cache = {k:v for (k,v) in self.cache.items() if k >= cur_cut}

        # print('frame_callback', t, descr)

def frame2time(fr, fps):
    s = fr / fps
    h = s // (60 * 60)
    m = (s // 60) % 60
    s = s % 60
    return "%d:%.2d:%06.3f" % (h, m, s)