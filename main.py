#!/usr/bin/env python3
import os
import pickle
import json
from argparse import ArgumentParser

import cv2
import numpy as np

from pprint import pprint


def extract_features(image, vector_size=32):
    try:
        alg = cv2.KAZE_create()
        kps = alg.detect(image)
        kps = sorted(kps, key=lambda x: -x.response)[:vector_size]
        kps, dsc, = alg.compute(image, kps)
        if dsc is None:
            dsc = np.asarray([])
        dsc = dsc.flatten()
        needed_size = (vector_size * 64)
        if dsc.size < needed_size:
            dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])
    except cv2.error as e:
        print('Error: ', e)
        return None

    return dsc


def load_video(video):
    dirpath = os.path.splitext(video)[0]
    if os.path.isdir(os.path.splitext(video)[0]):
        print("Processing {}...".format(video))
        video_data = []
        for image_file in [
                os.path.join(dirpath, f)
                for f in os.listdir(dirpath)
                if os.path.isfile(os.path.join(dirpath, f))
        ]:
            video_data.append(extract_features(cv2.imread(image_file)))
    else:
        os.mkdir(dirpath)
        vcap = cv2.VideoCapture(video)
        if vcap.isOpened():
            print("Processing {}...".format(video))
            vframes = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
            samples = np.random.randint(0, vframes, 1000)
            samples.sort()
            success, img = vcap.read()
            frame = 0
            video_data = []
            while success:
                if frame in samples:
                    print("  {:3}/1000".format(
                        np.where(samples == frame)[0][0]))
                    resized_img = cv2.resize(img, (100, 100))
                    video_data.append(extract_features(resized_img))
                    cv2.imwrite(
                        "{}/{}.png".format(dirpath,
                                           np.where(samples == frame)[0][0]),
                        resized_img)
                success, img = vcap.read()
                frame += 1
    return video_data


def main():
    parser = ArgumentParser('FilmCategorize')
    parser.add_argument('source', help="Source directory")
    args = parser.parse_args()
    args.files = [
        os.path.join(args.source, f)
        for f in os.listdir(args.source)
        if os.path.isfile(os.path.join(args.source, f))
    ]
    if not os.path.isfile("features.pkl"):
        data = {}
        for file in args.files:
            data[os.path.splitext(file)[0]] = load_video(file)
        with open("features.pkl", 'wb') as out_file:
            pickle.dump(data, out_file)
    else:
        with open("features.pkl", "rb") as in_file:
            data = pickle.load(in_file)
    nodes = []
    links = []
    link_weights = []
    for i, src in enumerate(data):
        print("Computing similarity for {}[{}]".format(src, i))
        nodes.append({"name": src, "group": i})
        for j, dest in enumerate(data):
            if j <= i:
                continue
            print("  {}".format(dest))
            weights = []
            for k, src_frame in enumerate(data[src]):
                for l, dest_frame in enumerate(data[dest]):
                    weights.append(np.dot(src_frame, dest_frame) / (np.power(0.02 * np.abs(k-l), 1.5) + 1))
            links.append({"source": i, "target": j, "value": 10 / (np.average(weights) - 1)})
            link_weights.append(10 / (np.average(weights) - 1))
            print("      {}".format(10 / (np.average(weights) - 1)))
    print("Trimming connections...\n")
    avg_weight = np.average(link_weights)
    trimed_links = []
    for link in links:
        if link["value"] >= avg_weight:
            trimed_links.append(link)
    with open("pcap_export.json", 'w') as out_file:
        json.dump({"nodes": nodes, "links": trimed_links}, out_file)

if __name__ == "__main__":
    main()
