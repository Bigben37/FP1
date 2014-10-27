import os

from data import DataErrors


class SquidData(DataErrors):

    def __init__(self):
        super(SquidData, self).__init__()
        self.even = False

    @classmethod
    def fromPath(cls, path, even):
        data = cls()
        data.path = path
        data.even = even
        if path:
            data.loadData()
        return data

    def loadData(self):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, self.path))
        with open(p, 'r') as f:
            first = True
            i = 0
            for row in f:
                if i > 0 and (i % 2 == 0) == self.even:
                    x, y = map(float, row.strip().split(',')[:2])
                    self.addPoint(x, y, 0, 0)
                i += 1
        self.setXErrorAbs(self.getMinDeltaX())
        self.setYErrorAbs(self.getMinDeltaY())

    def getMinDeltaX(self):
        """get x bin error"""
        deltas = set()
        for i in xrange(self.getLength() - 1):
            deltas.add(self.points[i + 1][0] - self.points[i][0])
        return min(deltas)

    def getMinDeltaY(self):
        """get y bin error"""
        deltas = set()
        for i in xrange(self.getLength() - 1):
            deltas.add(abs(self.points[i + 1][1] - self.points[i][1]))
        deltas.discard(0)
        return min(deltas)


def prepareGraph(g):
    """set unified graph style for graph with errors and a lot of data points"""
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)
