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
                    self.startCut(data['input'], data['output'])
        except Exception as e:
            self.log(traceback.format_exc())

    def startCut(self, input, output):
        rec_name = 'recordings/1.m3u8' # TODO: timestamps

        comb = Combinator(rec_name, output, self)
        self.log('main: created Combinator')
        desc = Descriptor(comb.scene_callback, self)
        self.log('main: created Descriptor')
        proc = Process(desc.frame_callback, self)
        self.log('main: created Process')
        ffmpeg = FFMpeg(input, rec_name, proc.pipe_w_sd, self)
        self.log('main: created FFMpeg')

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        # TODO: resume
        print(self.address, 'closed')

if __name__ == '__main__':
    server = SimpleWebSocketServer('127.0.0.1', 8000, WSServer)
    server.serveforever()
