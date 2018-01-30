import json

import cv2
import numpy
import skimage.draw


def draw_path(img, path, alpha=1.0):
    cur = (path[0] * img.shape[::-1]).astype(numpy.uint32)

    for pos in path[1:]:
        pos = (pos * img.shape[::-1]).astype(numpy.uint32)
        if pos[1] >= img.shape[0]:
            pos[1] = img.shape[0] - 1
        if pos[0] >= img.shape[1]:
            pos[0] = img.shape[1] - 1

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
    with open('data.json') as f:
        d = json.load(f)

    d = {
        k: [numpy.array(x) for x in d[k]]
        for k in d.keys()
    }

    return d


pathes = load_pathes()

size = 512
img = numpy.zeros((size, size))
for charset in pathes.values():
    for path in charset:
        draw_path(img, path, alpha=0.1)
cv2.imshow('all', img.astype(numpy.uint8))
cv2.waitKey(-1)
