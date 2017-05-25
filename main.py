#!/usr/bin/python
import argparse
import sys
import os

from combinator import Combinator
from descriptor import Descriptor
from ffmpeg import FFMpeg
from segmenter import Segmenter
from stip import STIP

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Media filename or URL")
    parser.add_argument("-wm", help="Calculate and write k-means data file")
    parser.add_argument("-kc", help="k-means precalc point count", type=int, default=1000)
    parser.add_argument("-rm", help="Read k-means data file")
    parser.add_argument("-t", help="Recording file", required=True)
    parser.add_argument("-o", help="Output file", required=True)
    args = parser.parse_args()

    if args.rm or args.wm:
        # TODO: do not segment if we're precalculating clusters
        comb = Combinator(args.t, args.o)
        desc = Descriptor(comb.scene_callback, wm=args.wm, rm=args.rm, kc=args.kc)
        segm = Segmenter(desc_cb=desc.cut_callback)
        stip = STIP(desc.callback)
        ffmpeg = FFMpeg(args.filename, args.t, segm.pipe_w_sd, stip.fifo)
    else:
        print('You should specify -rm or -wm')
        sys.exit(1)
