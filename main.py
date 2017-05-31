#!/usr/bin/python
import argparse
import json
import sys
import traceback
import os

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

from combinator import Combinator
from descriptor import Descriptor
from ffmpeg import FFMpeg
from process import Process

class WSServer(WebSocket):

    def sendJSON(self, m):
        self.sendMessage(json.dumps(m))

    def log(self, *m):
        self.sendMessage(json.dumps({'log': ' '.join(str(i) for i in m)}))

    def handleMessage(self):
        try:
            data = json.loads(self.data)
            print(data)
            if 'action' in data:
                if data['action'] == 'start':
                    self.startCut(data['input'])
                elif data['action'] == 'save':
                    self.saveRip(data['output'])
                elif data['action'] == 'markScene':
                    self.comb.markScene(data['id'], data['mark'])
        except Exception as e:
            self.log(traceback.format_exc())

    def startCut(self, input):
        rec_name = 'recordings/1.m3u8' # TODO: timestamps

        self.comb = Combinator(rec_name, self)
        print('main: created Combinator')
        self.desc = Descriptor(self.comb.scene_callback)
        print('main: created Descriptor')
        self.proc = Process(self.desc.frame_callback, self)
        print('main: created Process')
        self.ffmpeg = FFMpeg(input, rec_name, self.proc.pipe_w_sd)
        print('main: created FFMpeg')

    def saveRip(self, output):
        self.ffmpeg.kill()
        self.proc.do_stop = True
        self.comb.saveRip(output)

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        # TODO: resume
        print(self.address, 'closed')

if __name__ == '__main__':
    server = SimpleWebSocketServer('127.0.0.1', 8000, WSServer)
    print('Nice! Now go to file://%s/panel.html' % os.path.dirname(os.path.realpath(__file__)))
    server.serveforever()
