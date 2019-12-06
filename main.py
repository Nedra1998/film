#!/usr/bin/env python3
import os
from argparse import ArgumentParser

import cv2
import numpy as np


def load_video(video):
    if os.path.isdir(os.path.splitext(video)[0]):
        pass
    else:
        dirpath = os.path.splitext(video)[0]
        os.mkdir(dirpath)
        vcap = cv2.VideoCapture(video)
        if vcap.isOpened():
            print("Processing {}...".format(video))
            vwidth = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
            vheight = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            vframes = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
            samples = np.random.randint(0, vframes, 100)
            samples.sort()
            success, img = vcap.read()
            frame = 0
            while success:
                if frame in samples:
                    print("  {:3}/100".format(
                        np.where(samples == frame)[0][0]))
                    cv2.imwrite(
                        "{}/{}.png".format(dirpath,
                                           np.where(samples == frame)[0][0]),
                        cv2.resize(img, (100, 100)))
                success, img = vcap.read()
                frame += 1


def main():
    parser = ArgumentParser('FilmCategorize')
    parser.add_argument('source', help="Source directory")
    args = parser.parse_args()
    args.files = [
        os.path.join(args.source, f)
        for f in os.listdir(args.source)
        if os.path.isfile(os.path.join(args.source, f))
    ]
    for file in args.files:
        load_video(file)
    print(args)


if __name__ == "__main__":
    main()
