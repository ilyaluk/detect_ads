import cv2
import threading
import time
import os
import subprocess
import tempfile

import detector

class Segmenter(object):
    def __init__(self, cut_cb=None, save_path=None):
        self.pipe_r_hd, self.pipe_w_hd = os.pipe()
        os.set_inheritable(self.pipe_w_hd, True)

        self.pipe_r_sd, self.pipe_w_sd = os.pipe()
        os.set_inheritable(self.pipe_w_sd, True)

        self.cut_cb = cut_cb
        self.save_path = save_path
        self.cuts = set()

        self.processed = -1

        detect = threading.Thread(target=self.loop)
        write = threading.Thread(target=self.loop_write)
        detect.start()
        write.start()

    def loop(self):
        cap_sd = cv2.VideoCapture('pipe:%d' % self.pipe_r_sd)

        det = detector.ContentDetector()
        i = 0
        while cap_sd.isOpened():
            ret, frame = cap_sd.read()
            is_cut = det.process_frame(i, frame)

            self.cut_cb(i, is_cut)
            if is_cut:
                self.cuts.add(i)
            self.processed = i

            i += 1

        cap_sd.release()

    def loop_write(self):
        cap_hd = cv2.VideoCapture('pipe:%d' % self.pipe_r_hd)
        width  = int(cap_hd.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap_hd.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = int(cap_hd.get(cv2.CAP_PROP_FPS))


        chunk_id = 0
        i = 0

        pipe_r_chunk, pipe_w_chunk = os.pipe()
        os.set_inheritable(pipe_r_chunk, True)
        proc = subprocess.Popen(['ffmpeg', '-y', '-f', 'rawvideo', '-pixel_format', 'bgr24',
            '-video_size', '%dx%d' % (width, height), '-framerate', '24',
            '-i', 'pipe:%d' % pipe_r_chunk,
            self.save_path % chunk_id],
            stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
            close_fds=False)
        tmp_raw = os.fdopen(pipe_w_chunk, 'wb')

        while cap_hd.isOpened():
            while i > self.processed:
                time.sleep(0.1)

            ret, frame_full_res = cap_hd.read()

            if i in self.cuts:
                chunk_id += 1
                self.cuts.remove(i)

                tmp_raw.close()
                proc.wait()
                os.close(pipe_r_chunk)

                pipe_r_chunk, pipe_w_chunk = os.pipe()
                os.set_inheritable(pipe_r_chunk, True)
                proc = subprocess.Popen(['ffmpeg', '-y', '-f', 'rawvideo', '-pixel_format', 'bgr24',
                    '-video_size', '%dx%d' % (width, height), '-framerate', '24',
                    '-i', 'pipe:%d' % pipe_r_chunk,
                    self.save_path % chunk_id],
                    stdin=None, stdout=None, stderr=open('/dev/null', 'wb'),
                    close_fds=False)
                tmp_raw = os.fdopen(pipe_w_chunk, 'wb')

            fp = tempfile.TemporaryFile()
            frame_full_res.tofile(fp)
            fp.seek(0)
            tmp_raw.write(fp.read())
            fp.close()
            i += 1

        cap_hd.release()
