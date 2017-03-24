# import cv2
import numpy as np
import time

class Combinator(object):
    def __init__(self, chunk_format, output_file):
        self.chunk_format = chunk_format
        self.output = open(output_file, 'wb')
        # self.debug_file = open('debug.csv', 'w')

        self.is_ads = False
        self.chunk_id = 0

        self.window = 15 # frames

        self.cuts = set()
        self.start_descs = dict()
        self.end_descs = dict()
        self.cache = dict()
        self.processed = -1

    def cut_callback(self, t, is_cut):
        self.processed = t
        print('comb cut', frame2time(t, 24))
        if is_cut:
            self.cuts.add(t)

    def frame_callback(self, t, descr):
        while t + self.window + 1 > self.processed:
            time.sleep(0.1)

        print('comb frame', frame2time(t, 24))

        self.cache[t] = descr

        while len(self.cuts) and min(self.cuts) <= t - self.window + 1:
            cur_cut = min(self.cuts)
            self.cuts.remove(cur_cut)

            start_desc = np.array([])
            for i in range(0, self.window):
                if cur_cut + i in self.cache:
                    start_desc = np.hstack((start_desc, self.cache[cur_cut + i]))
                else:
                    start_desc = np.hstack((start_desc, np.zeros(len(descr))))
            # self.start_descs[cur_cut] = start_desc

            end_desc = np.array([])
            for i in range(-self.window, 0):
                if cur_cut + i in self.cache:
                    end_desc = np.hstack((end_desc, self.cache[cur_cut + i]))
                else:
                    end_desc = np.hstack((end_desc, np.zeros(len(descr))))
            # self.end_descs[cur_cut] = end_desc

            if not self.is_ads and False: # some check if start_desc is start of ads
                self.is_ads = True

            if self.is_ads and False: # some check if end_desc is end of ads
                self.is_ads = False

            if not self.is_ads:
                with open(self.chunk_format % self.chunk_id, 'rb') as chunk:
                    self.output.write(chunk.read())

            # self.debug_file.write('%d,s,%s\n' % (cur_cut, ','.join(str(i) for i in start_desc)))
            # self.debug_file.write('%d,e,%s\n' % (cur_cut, ','.join(str(i) for i in end_desc)))

            self.chunk_id += 1
            self.cache = {k:v for (k,v) in self.cache.items() if k >= cur_cut}

def frame2time(fr, fps):
    s = fr / fps
    h = s // (60 * 60)
    m = (s // 60) % 60
    s = s % 60
    return "%d:%.2d:%06.3f" % (h, m, s)