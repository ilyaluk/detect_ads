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
        print('Descriptor', t, len(points))
        if self.wm is not None:
            for pt in points:
                if self.points is None:
                    self.points = np.array(pt[5] + pt[6])
                else:
                    self.points = np.vstack((self.points, np.array(pt[5] + pt[6])))
                self.processed += 1
                if self.processed >= self.kc:
                    kmeans = KMeans(n_clusters=self.K).fit(self.points)
                    # print(kmeans.labels_)
                    # print(kmeans.cluster_centers_)
                    pickle.dump(kmeans, open(self.wm, 'wb'))
                    print('Precalculated and saved k-means.')
                    print('Now try to run with -rm %s!' % self.wm)
                    sys.exit(0)
        if self.kmeans is not None:
            tmp = [pt[5] + pt[6] for pt in points]
            labels = self.kmeans.predict(tmp)
            # print(labels)
            hist, _ = np.histogram(labels, 10, (-0.5, self.K - 0.5), density=True)
            # print(hist)
            self.frame_cb(t, hist)
