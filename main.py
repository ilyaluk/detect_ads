#!/usr/bin/python3
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
        text = ' '.join(str(i) for i in m)
        print(text)
        self.sendMessage(json.dumps({'log': text}))

    def error(self, *m):
        text = ' '.join(str(i) for i in m)
        print(text)
        self.sendMessage(json.dumps({'error': text}))

    def handleMessage(self):
        try:
            data = json.loads(self.data)
            if 'action' in data:
                if data['action'] == 'start':
                    self.startCut(data['input'])
                elif data['action'] == 'save':
                    self.saveRip(data['output'])
                elif data['action'] == 'markScene':
                    self.comb.markScene(data['id'], data['mark'])
        except Exception as e:
            self.error(traceback.format_exc())

    def startCut(self, input):
        rec_name = 'recordings/1.m3u8' # TODO: timestamps

        self.comb = Combinator(rec_name, self)
        self.log('main: created Combinator')
        self.desc = Descriptor(self.comb.scene_callback)
        self.log('main: created Descriptor')
        self.proc = Process(self.desc.frame_callback, self)
        self.log('main: created Process')
        self.ffmpeg = FFMpeg(input, rec_name, self.proc.pipe_w_sd)
        self.log('main: created FFMpeg')

    def saveRip(self, output):
        self.ffmpeg.kill()
        self.proc.do_stop = True
        self.comb.saveRip(output)

    def handleConnected(self):
        self.log(self.address, 'connected')

    def handleClose(self):
        # TODO: resume
        self.log(self.address, 'closed')

if __name__ == '__main__':
    server = SimpleWebSocketServer('127.0.0.1', 8000, WSServer)
    print('Nice! Now go to file://%s/panel.html' % os.path.dirname(os.path.realpath(__file__)))
    server.serveforever()
