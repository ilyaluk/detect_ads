#!/usr/bin/python
import sys
import os

# from combinator import Combinator
from descriptor import Descriptor
from ffmpeg import FFMpeg
from segmenter import Segmenter
from stip import STIP

if __name__ == '__main__':
    # http://stream.sunnysubs.com/stream/old3/spz240.m3u8
    if len(sys.argv) < 2:
        sys.stderr.write('Specify filename or URL in first argument\n')
        sys.exit(1)

    segm = Segmenter()
    desc = Descriptor()
    stip = STIP(desc.callback)
    ffmpeg = FFMpeg(sys.argv[1], segm.pipe_w_hd, segm.pipe_w_sd, stip.fifo)
