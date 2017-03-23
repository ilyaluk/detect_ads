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
    # http://stream.sunnysubs.com/stream/old3/spz240.m3u8
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Media filename or URL")
    parser.add_argument("-wm", help="Calculate and write k-means data file")
    parser.add_argument("-kc", help="k-means precalc point count", type=int, default=1000)
    parser.add_argument("-rm", help="Read k-means data file")
    parser.add_argument("-s", help="Split video")
    parser.add_argument("-rs", help="Read splitted video")
    args = parser.parse_args()

    if not args.rm and not args.wm:
        print('You should specify -rm or -wm')
        sys.exit(1)

    if args.s:
        segm = Segmenter(comb.cut_callback)
        ffmpeg = FFMpeg(args.filename, segm.pipe_w_hd, segm.pipe_w_sd, stip.fifo)
    elif args.rs:
        comb = Combinator(args.filename)
        segm = Segmenter(comb.cut_callback)
        desc = Descriptor(comb.frame_callback, wm=args.wm, rm=args.rm, kc=args.kc)
        stip = STIP(desc.callback)
        ffmpeg = FFMpeg(args.filename, segm.pipe_w_hd, segm.pipe_w_sd, stip.fifo)
    else:
        print('You should specify -s or -rs')
        sys.exit(1)
