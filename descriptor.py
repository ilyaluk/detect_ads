from sklearn.cluster import KMeans
import numpy as np
import pickle
import sys

class Descriptor(object):
    def __init__(self, frame_cb, wm=None, rm=None, kc=None):
        self.frame_cb = frame_cb
        self.wm = self.rm = None
        self.K = 10
        if wm is not None:
            self.wm = wm
            self.kc = kc
            self.processed = 0
            self.points = None
            self.kmeans = None
        if rm is not None:
            self.kmeans = pickle.load(open(rm, 'rb'))

    def callback(self, t, points):
        print('Descr', t, len(points))
        if self.wm is not None:
            # do not stack every point
            for pt in points:
                if self.points is None:
                    self.points = np.array(pt)
                else:
                    self.points = np.vstack((self.points, np.array(pt)))
                self.processed += 1
                if self.processed % 10 == 0:
                    print("Precalc: about %.2f%% done" % (100 * self.processed / self.kc))
                if self.processed >= self.kc:
                    kmeans = KMeans(n_clusters=self.K).fit(self.points)
                    pickle.dump(kmeans, open(self.wm, 'wb'))
                    print('Precalculated and saved k-means.')
                    print('Now try to run with -rm %s!' % self.wm)
                    sys.exit(0)
        if self.kmeans is not None:
            labels = self.kmeans.predict(points)
            hist, _ = np.histogram(labels, 10, (-0.5, self.K - 0.5), density=True)
            # print(labels)
            # print(hist)
            self.frame_cb(t, hist)
