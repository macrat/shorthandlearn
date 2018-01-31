import chainer
import chainer.functions as F
import chainer.links as L
import numpy

import util


class Classifier(chainer.Chain):
    def __init__(self):
        super().__init__(
            conv1=L.Convolution2D(1, 16, 2),
            conv2=L.Convolution2D(16, 32, 2),
            conv3=L.Convolution2D(32, 64, 2),
            l1=L.Linear(256, 128),
            l2=L.Linear(128, 45),
        )

        self.optimizer = chainer.optimizers.Adam()
        self.optimizer.setup(self)

    def predict(self, x):
        x = chainer.Variable(x)
        h = F.max_pooling_2d(F.relu(self.conv1(x)), 2)
        h = F.max_pooling_2d(F.relu(self.conv2(h)), 2)
        h = F.max_pooling_2d(F.relu(self.conv3(h)), 2)
        h = F.relu(self.l1(h))
        h = self.l2(h)
        return h

    def fit(self, x, y):
        y = chainer.Variable(y)
        h = self.predict(x)
        self.zerograds()
        loss = F.softmax_cross_entropy(h, y)
        accuracy = F.accuracy(h, y)
        loss.backward()
        self.optimizer.update()
        return h.data, accuracy.data


def make_data(size):
    data = util.load_pathes()
    data = util.trim_short(data)
    data = util.increase(data)
    labels, images = util.learn_data(data, size=size)

    #labels = [x for x in labels if x in 'あかさたなはまやらわ']
    #images = numpy.array([x for l, x in zip(labels, images) if l in 'あかさたなはまやらわ'])

    keys = sorted(data.keys())

    labels = numpy.array([keys.index(x) for x in labels], dtype=numpy.int32)
    images = (images / 255).reshape(-1, 1, size, size).astype(numpy.float32)

    return labels, images


if __name__ == '__main__':
    model = Classifier()

    labels, images = make_data(16)
    keys = numpy.random.random(len(labels)) > 0.1

    train = images[keys], labels[keys]
    test = images[numpy.logical_not(keys)], labels[numpy.logical_not(keys)]

    with open('log.csv', 'w') as log:
        for i in range(500):
            h, acc = model.fit(*train)

            acc2 = F.accuracy(model.predict(test[0]), test[1]).data

            print('{},{},{}'.format(i, acc, acc2), file=log)
            print('{:4d}: {:7.2%} {:7.2%}'.format(i, float(acc), float(acc2)))

    data = util.load_pathes()
    keys = sorted(data.keys())
    result = []
    for text in keys:
        pathes = data[text]
        images = numpy.array([util.to_image(path, size=16) for path in pathes])
        images = (images / 255).reshape(-1, 1, 16, 16).astype(numpy.float32)
        result.append([text, sum(model.predict(images).data.argmax(1) == keys.index(text)) / len(images)])

    result.sort(key=lambda x: x[1])
    for text, rate in result:
        print('{}: {:7.2%}'.format(text, rate))
