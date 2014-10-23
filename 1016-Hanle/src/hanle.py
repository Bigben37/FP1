from data import DataErrors
import os
import numpy as np


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
            sx = x * 0.01
            self.points[i] = (x, y, sx, sy)


class TauData(DataErrors):
    ST = 2

    def loadData(self):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, self.path))
        with open(p, 'r') as f:
            for row in f:
                T, tau, stau = map(float, row.strip().split('\t'))
                p = TempToPressure(T)
                sp = TauData.ST / (273.15 + T)  # in Kelvin
                self.addPoint(p, tau, sp, stau)


def TempToPressure(T):
    T2 = 273.15 + T
    pc = 167000000.
    Tc = 1764.
    Tr = 1. - T2 / Tc
    a1 = -4.57618368
    a2 = -1.40726277
    a3 = 2.36263541
    a4 = -31.0889985
    a5 = 58.0183959
    a6 = -27.6304546
    return 1000 * pc * np.exp((Tc / T2) * (a1 * Tr + a2 * Tr ** 1.89 + a3 * Tr ** 2 + a4 * Tr ** 8 +
                                           a5 * Tr ** 8.5 + a6 * Tr ** 9))


def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)
