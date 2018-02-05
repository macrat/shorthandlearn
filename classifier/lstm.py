import chainer
import chainer.functions as F
import chainer.links as L
import numpy

import util


class LSTMClassifier(chainer.Chain):
    def __init__(self):
        super().__init__(
            lstm=L.LSTM(2, 12),
            l1=L.Linear(12, 24),
            l2=L.Linear(24, 45),
        )

        self.optimizer = chainer.optimizers.Adam()
        self.optimizer.setup(self)

    def predict(self, x):
        self.reset()

        for v in x:
            h = self.lstm(v.reshape((1, 2)))
            h = self.l1(h)
            h = self.l2(h)

        return h.data

    def fit(self, x, y):
        self.reset()

        loss = 0
        for v in x:
            h = self.lstm(v.reshape((1, 2)))
            h = self.l1(h)
            h = self.l2(h)
            loss += F.softmax_cross_entropy(h, y)

        self.zerograds()
        loss.backward()
        self.optimizer.update()

        return h.data, F.softmax_cross_entropy(h, y).data

    def reset(self):
        self.lstm.reset_state()


def load_data():
    result = []

    data = util.load_pathes().values()
    for i, xs in enumerate(data):
        for x in xs:
            result.append((numpy.array(x, dtype=numpy.float32), numpy.array([i], dtype=numpy.int32)))

    return result


if __name__ == '__main__':
    model = LSTMClassifier()

    data = load_data()
    keys = numpy.random.random(len(data)) > 0.1

    train = [x for i, x in enumerate(data) if keys[i]]
    test = [x for i, x in enumerate(data) if not keys[i]]

    with open('log.csv', 'w') as log:
        for i in range(500):
            loss = sum(model.fit(x, y)[1] for x, y in train)
            loss2 = sum(F.softmax_cross_entropy(model.predict(x), y).data for x, y in test)

            print('{},{},{}'.format(i, loss / len(train), loss2 / len(test)), file=log)
            print('{:4d}: {} {}'.format(i, loss / len(train), loss2 / len(test)))
