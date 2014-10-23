import os

from data import DataErrors

import numpy as np

STEMP = 2
serieslabels = {0: 'Tag 1, abk#ddot{u}hlen', 1: 'Tag 2, abk#ddot{u}hlen', 2: 'Tag 2, aufw#ddot{a}rmen'}
seriescolors = [4, 1, 3]


class HanleData(DataErrors):

    def __init__(self):
        super(HanleData, self).__init__()
        self.channel = 1

    @classmethod
    def fromPath(cls, path, channel):
        data = cls()
        data.path = path
        data.channel = channel
        if path:
            data.loadData()
        return data

    def loadData(self):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, self.path))
        isHeader = True
        with open(p, 'r') as f:
            for row in f:
                if isHeader:
                    isHeader = False
                else:
                    data = map(lambda x: float(x.replace(',', '.')), row.strip().split('\t'))
                    x = data[0]
                    y = data[self.channel]
                    self.addPoint(x, y, 0, 0)
        self.setXErrorAbs(self.getMinDeltaX() / 2)
        self.setYErrorAbs(self.getMinDeltaY() / 2)

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

    def convertTimeToB(self, fit):
        for i in xrange(self.getLength()):
            x, y, sx, sy = self.getPoint(i)
            x = fit.Eval(x) * 3.363e-4 * 1000  # in mT
            sx = abs(x) * 0.01
            self.points[i] = (x, y, sx, sy)


def TempToSeries(T):
    series = [[23, 19, 14], [7, 5, 0, -1, -3, -4, -7, -8], [3, 10]]
    for i, s in enumerate(series):
        if T in s:
            return i
    return None


def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)

def setMultiGraphTitle(mg, xtitle, ytitle):
    mg.GetXaxis().SetTitle(xtitle)
    mg.GetXaxis().CenterTitle()
    mg.GetYaxis().SetTitle(ytitle)
    mg.GetYaxis().CenterTitle()
