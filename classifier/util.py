import json

import cv2
import numpy
import skimage.draw


def draw_path(img, path, alpha=1.0):
    cur = (path[0] * img.shape[::-1]).astype(numpy.uint32)
    if cur[1] >= img.shape[0]:
        cur[1] = img.shape[0] - 1
    if cur[0] >= img.shape[1]:
        cur[0] = img.shape[1] - 1
    cur[cur < 0] = 0

    for pos in path[1:]:
        pos = (pos * img.shape[::-1]).astype(numpy.uint32)
        if pos[1] >= img.shape[0]:
            pos[1] = img.shape[0] - 1
        if pos[0] >= img.shape[1]:
            pos[0] = img.shape[1] - 1
        pos[pos < 0] = 0

        r, c = skimage.draw.line(cur[1], cur[0], pos[1], pos[0])
        d = (img[r, c] * (1 - alpha)) + (255 * alpha)
        d[d > 255] = 255
        d[d < 0] = 0
        img[r, c] = d
        cur = pos


def to_image(path, size=256):
    img = numpy.zeros((size, size))

    draw_path(img, path)

    return (255 - img).astype(numpy.uint8)


def load_pathes():
    with open('../data.json') as f:
        d = json.load(f)

    d = {
        k: [numpy.array(x) for x in d[k]]
        for k in d.keys()
    }

    return d


def learn_data(data, size=64):
    images = []
    labels = []

    for text, pathes in data.items():
        for path in pathes:
            labels.append(text)
            images.append(to_image(path, size=size))

    return labels, numpy.array(images)


def increase(data):
    data = dict(data)
    for text, pathes in data.items():
        newdata = []
        for p in pathes:
            newdata.append(p + [0.1, 0])
            newdata.append(p - [0.1, 0])
            newdata.append(p + [0, 0.1])
            newdata.append(p - [0, 0.1])
            #newdata.append(p + [0.1, 0.1])
            #newdata.append(p - [0.1, 0.1])
            #newdata.append(p + [0.1, -0.1])
            #newdata.append(p + [-0.1, 0.1])
        pathes.extend(newdata)
    return data


def path_length(path):
    return numpy.sqrt(((path[:-1] - path[1:]) ** 2).sum(axis=1)).sum()


def trim_short(data, threshold=0.01):
    return {
        text: [p for p in pathes if path_length(p) > threshold]
        for text, pathes in data.items()
    }
