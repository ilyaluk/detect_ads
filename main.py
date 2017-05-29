#!/usr/bin/python
import argparse
import sys
import os

from combinator import Combinator
from descriptor import Descriptor
from ffmpeg import FFMpeg
from process import Process

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Media filename or URL")
    parser.add_argument("output", help="Output file")
    # parser.add_argument("-t", help="Recording file", required=True)
    rec_name = 'recordings/1.m3u8' # TODO: timestamps
    args = parser.parse_args()

    comb = Combinator(rec_name, args.output)
    print('main: created Combinator')
    desc = Descriptor(comb.scene_callback)
    print('main: created Descriptor')
    proc = Process(desc_cb=desc.frame_callback)
    print('main: created Process')
    ffmpeg = FFMpeg(args.input, rec_name, proc.pipe_w_sd)
    print('main: created FFMpeg')
