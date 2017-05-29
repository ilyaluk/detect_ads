import numpy as np

class Descriptor(object):
    def __init__(self, scene_cb):
        self.scene_cb = scene_cb
        self.processed = 0
        self.points = None

    def frame_callback(self, t, points, is_cut):
        if points is None:
            points = []
        elif self.points is None:
            self.points = points.sum(axis=0)
        else:
            self.points += points.sum(axis=0)

        print('desc: ', t, len(points))

        if is_cut:
            print('desc: cut', t)

            if self.points is None:
                self.points = np.zeros(64)

            self.scene_cb(t, self.points)
            self.points = None
