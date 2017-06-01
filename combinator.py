# import cv2
import numpy as np
import time
import subprocess

class Combinator(object):
    def __init__(self, rec_file, ws):
        self.rec_file = rec_file

        self.debug_file = open('debug.csv', 'w')

        self.is_ads = False
        self.chunk_id = 0

        self.start_descs = {67: None, 68: None}
        self.end_descs = {170: None}
        self.ignored = set()
        self.descs = []
        self.scene_timecodes = []
        self.scene_status = {}

        self.ws = ws

    def scene_callback(self, t, descr):
        print('Comb', t, descr)

        id = len(self.descs)
        if id in self.start_descs and self.start_descs[id] == None:
            self.start_descs[id] = descr
        if id in self.end_descs and self.end_descs[id] == None:
            self.end_descs[id] = descr

        self.descs.append(descr)
        self.scene_timecodes.append(t)
        self.debug_file.write('%d,%s\n' % (t, ','.join(str(i) for i in descr)))

        self.updateScene(id)

    def updateScene(self, id):
        tmp = ''
        if id not in self.ignored:
            for i in list(self.start_descs):
                if i <= id and self.start_descs[i] is not None:
                    corr, sim = compareDescs(self.descs[id], self.start_descs[i])
                    if corr > 0.9 and sim < 0.02:
                        self.scene_status[id] = 'adstart'
                        tmp += 'ADSTART<br>'
                        self.start_descs[id] = self.descs[id]
                    tmp += '<a href="#scene%d">%d</a> %f %f<br>' % (i, i, corr, sim)

            for i in list(self.end_descs):
                if i <= id and self.end_descs[i] is not None:
                    corr, sim = compareDescs(self.descs[id], self.end_descs[i])
                    if corr > 0.9 and sim < 0.02:
                        self.scene_status[id] = 'adend'
                        tmp += 'ADEND<br>'
                        self.end_descs[id] = self.descs[id]
                    tmp += '<a href="#scene%d">%d</a> %f %f<br>' % (i, i, corr, sim)

        if id not in self.scene_status:
            for i in range(id - 1, -1, -1):
                if i in self.scene_status:
                    if self.scene_status[i] in ('ads', 'adstart'):
                        self.scene_status[id] = 'ads'
                    break

        if id not in self.scene_status:
            self.scene_status[id] = 'content'

        tmp += '<b>%s</b>' % self.scene_status[id]

        self.ws.sendJSON({
            'update': id,
            'text': tmp
        })

    def markScene(self, id, mark):
        if mark == 'adStart':
            self.ignored.remove(id)
            self.start_descs[id] = self.descs[id] if id < len(self.descs) else None
        elif mark == 'adEnd':
            self.ignored.remove(id)
            self.end_descs[id] = self.descs[id] if id < len(self.descs) else None
        elif mark == 'unmark':
            self.ignored.add(id)
            if id in self.start_descs:
                del self.start_descs[id]
            if id in self.end_descs:
                del self.end_descs[id]

        if id < len(self.descs):
            # for i in range(id, len(self.descs)):
            for i in range(len(self.descs)):
                del self.scene_status[i]
                self.updateScene(i)

    def saveRip(self, output):
        print('Saving rip to', output)
        isAds = True
        currentStart = ''
        fragid = 0

        for i in range(len(self.descs) + 1):
            if i < len(self.descs) and self.scene_status[i] == 'content':
                if isAds:
                    isAds = False
                    # TODO: solve problems
                    currentStart = frame2time(self.scene_timecodes[i], 24)
                    if i == 0:
                        currentStart = frame2time(0, 1)
            elif not isAds:
                if i < len(self.descs):
                    isAds = True
                    # TODO: solve problems
                    end = frame2time(self.scene_timecodes[i] - 5, 24)
                    print('Fragment: %s-%s' % (currentStart, end))
                    print('Transcoding...')
                    subprocess.call(['ffmpeg', "-y", "-threads", "0", "-live_start_index", "0",
                                     "-i", self.rec_file, "-ss", currentStart, "-to", end,
                                     "-bsf:a", "aac_adtstoasc", "-strict", "-2", "cut%d.mp4" % fragid],
                                    stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
                    fragid += 1
                else:
                    print('Found fragment: %s-' % currentStart)
                    print('Transcoding...')
                    subprocess.call(['ffmpeg', "-y", "-threads", "0", "-live_start_index", "0",
                                     "-i", self.rec_file, "-ss", currentStart,
                                     "-bsf:a", "aac_adtstoasc", "-strict", "-2", "cut%d.mp4" % fragid],
                                    stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
                    fragid += 1

        print('Merging...')
        open('concat.txt', 'w').write('\n'.join("file 'cut%d.mp4'" % i for i in range(fragid)))
        subprocess.call(['ffmpeg', "-y", "-threads", "0", "-f", "concat", "-i", "concat.txt",
                         "-c:v", "copy", '-c:a', 'copy', "-strict", "-2", output],
                        stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        print('Done!')

def compareDescs(d1, d2):
    prob1 = np.corrcoef(d1, d2)[0][1]
    prob2 = (abs(d1 - d2)).sum() / ((d1 + d2).sum())
    return prob1, prob2

def frame2time(fr, fps):
    s = fr / fps
    h = s // (60 * 60)
    m = (s // 60) % 60
    s = s % 60
    return "%d:%.2d:%06.3f" % (h, m, s)
