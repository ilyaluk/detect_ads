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
    parser.add_argument("filename", help="Media filename or URL")
    parser.add_argument("-wm", help="Calculate and write k-means data file")
    parser.add_argument("-kc", help="k-means precalc point count", type=int, default=1000)
    parser.add_argument("-rm", help="Read k-means data file")
    # parser.add_argument("-t", help="Recording file", required=True)
    rec_name = 'recordings/1.m3u8' # TODO: timestamps
    parser.add_argument("-o", help="Output file", required=True)
    args = parser.parse_args()

    if args.rm or args.wm:
        # TODO: do not segment if we're precalculating clusters
        comb = Combinator(rec_name, args.o)
        print('Created Combinator')
        desc = Descriptor(comb.scene_callback, wm=args.wm, rm=args.rm, kc=args.kc)
        print('Created Descriptor')
        proc = Process(desc_cb=desc.scene_callback)
        print('Created Process')
        ffmpeg = FFMpeg(args.filename, rec_name, proc.pipe_w_sd)
        print('Created FFMpeg')
    else:
        print('You should specify -rm or -wm')
        sys.exit(1)
