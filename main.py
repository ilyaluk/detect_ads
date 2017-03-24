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
    parser.add_argument("-c", help="Chunk file pattern, e.g. chunk%%04d.ts", required=True)
    parser.add_argument("-o", help="Output file, .ts", required=True)
    args = parser.parse_args()

    if args.wm:
        # TODO: do not segment if we're precalculating clusters
        comb = Combinator(args.c, args.o)
        desc = Descriptor(comb.scene_callback, wm=args.wm, rm=args.rm, kc=args.kc)
        segm = Segmenter(cut_cb=desc.cut_callback, save_path=args.c)
        stip = STIP(desc.callback)
        ffmpeg = FFMpeg(args.filename, segm.pipe_w_hd, segm.pipe_w_sd, stip.fifo)
    elif args.rm:
        comb = Combinator(args.c, args.o)
        desc = Descriptor(comb.scene_callback, wm=args.wm, rm=args.rm, kc=args.kc)
        segm = Segmenter(cut_cb=desc.cut_callback, save_path=args.c)
        stip = STIP(desc.callback)
        ffmpeg = FFMpeg(args.filename, segm.pipe_w_hd, segm.pipe_w_sd, stip.fifo)
    else:
        print('You should specify -rm or -wm')
        sys.exit(1)
