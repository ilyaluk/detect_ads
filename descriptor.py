from sklearn.cluster import KMeans
import numpy as np
import pickle
import sys

class Descriptor(object):
    def __init__(self, scene_cb, wm=None, rm=None, kc=None):
        self.scene_cb = scene_cb
        self.wm = None
        self.K = 10
        self.cuts = set()
        self.processed = 0
        self.points = None

        if wm is not None:
            self.wm = wm
            self.kc = kc
            self.kmeans = None
        if rm is not None:
            self.kmeans = pickle.load(open(rm, 'rb'))

    def scene_callback(self, t, points, is_cut):
        print('Descr', t, len(points))

        if is_cut:
            print('Descriptor cut', t)
            self.cuts.add(t)

        if self.kmeans is not None:
            self.cuts.remove(t - i)
            labels = self.kmeans.predict(self.points)
            hist, _ = np.histogram(labels, self.K, (-0.5, self.K - 0.5), density=True)
            self.points = None
            # print(labels)
            # print(hist)
            self.scene_cb(t - i, hist)

        if self.points is None:
            self.points = np.array(points)
        else:
            self.points = np.vstack((self.points, np.array(points)))

        if self.wm is not None:
            # do not stack every point
            self.processed += len(points)
            print("Precalc: about %.2f%% done" % (100 * self.processed / self.kc))
            if self.processed >= self.kc:
                kmeans = KMeans(n_clusters=self.K).fit(self.points)
                pickle.dump(kmeans, open(self.wm, 'wb'))
                print('Precalculated and saved k-means.')
                print('Now try to run with -rm %s!' % self.wm)
                sys.exit(0)
