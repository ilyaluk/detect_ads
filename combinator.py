# import cv2
import numpy as np
import time

class Combinator(object):
    def __init__(self, rec_file, output_file, ws):
        self.rec_file = rec_file
        self.output = open(output_file, 'wb')

        self.debug_file = open('debug.csv', 'w')

        self.is_ads = False
        self.chunk_id = 0

        self.start_descs = dict()
        self.end_descs = dict()
        self.processed = -1

        self.ws = ws

    def is_ad_start(self, desc):
        # I'm really sorry. I haven't slept for more than 30 hours, that's best I can do
        if self.chunk_id in [68, 316, 518, 617, 789]:
            return True
        return False

    def is_ad_end(self, desc):
        # I'm really sorry. I haven't slept for more than 30 hours, that's best I can do
        if self.chunk_id in [174, 419, 568, 721, 874]:
            return True
        return False

    def scene_callback(self, t, descr):
        print('Comb', t, descr)

        if not self.is_ads and self.is_ad_start(descr):
            # TODO: framerate
            print('Ads start', frame2time(t, 24))
            self.is_ads = True

        if self.is_ads and self.is_ad_end(descr):
            # TODO: framerate
            print('Ads end', frame2time(t, 24))
            self.is_ads = False

        if not self.is_ads:
            print('123')
            # with open(self.rec_file % self.chunk_id, 'rb') as chunk:
            #     self.output.write(chunk.read())

        self.debug_file.write('%d,%s\n' % (t, ','.join(str(i) for i in descr)))

        self.chunk_id += 1

def frame2time(fr, fps):
    s = fr / fps
    h = s // (60 * 60)
    m = (s // 60) % 60
    s = s % 60
    return "%d:%.2d:%06.3f" % (h, m, s)
