#!/usr/bin/python2.7
from data import DataErrors
import os
import csv
import numpy as np


class P1SemiCon(DataErrors):
    CTIME = 0
    CANGLE = 1
    CPYRO = 2
    CSAMPLE = 3
    CWAVELENGTH = 4
    CENERGY = 5
    LABELS = ('Zeit t / s', 'Winkel #alpha / {}^{#circ}', 'Spannung U / V', 'Spannung U / V',
              'Wellenl#ddot{a}nge #lambda / nm', 'Energie E / eV')

    def __init__(self):
        super(P1SemiCon, self).__init__()
        self.channels = ()

    @classmethod
    def fromPath(cls, path, channels):
        data = cls()
        data.path = path
        data.channels = channels
        if path:
            try:
                data.loadData()
            except NameError:
                print(data.__class__.__name__ + ".loadData() not in scope! Please implement. ")
        return data

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            isData = False
            for row in f:
                row = row.strip()
                if isData:
                    if row == 'Vernier Format 2':
                        isData = False
                    elif not row == '':
                        row = row.replace(',', '.').split('\t')
                        if len(row) == 6:
                            x = float(row[self.channels[0]])
                            y = float(row[self.channels[1]])
                            self.addPoint(x, y, 0, 0)
                else:
                    if row == '':
                        isData = True

    def getNeighbors(self, x):
        lower = self.points[0]
        for point in self.points:
            if point[0] > x:
                return lower, point
            lower = point
        return lower, lower

    def getIntpolYValue(self, x, lower, higher):
        x1, y1 = lower[:2]
        x2, y2 = higher[:2]
        m = (y2 - y1) / (x2 - x1)
        y = y1 + m * (x - x1)
        return y, 0.5 * (lower[4] + higher[4])

    def subtractUnderground(self, underground):
        for i in xrange(0, self.getLength()):
            x, y, sx, sy = self.points[i]
            print(x, y, underground.getNeighbors(x))
            #u, su = underground.getIntpolYValue(x, *underground.getNeighbors(x))
            #self.points[i] = (x, y - u, sx, np.sqrt(sy ** 2 + su ** 2))


class P2SemiCon(DataErrors):

    UERROR = 1

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                x, y = row[3:5]
                self.addPoint(float(x), float(y), 0, 0.0001)

    def subtractUnderground(self, a, b, sa, sb, rho):
        u = DataErrors()
        for x, sx in zip(self.getX(), self.getEX()):
            u.addPoint(x, a + b * x, sx, sa ** 2 + (x * sb) ** 2 + (b * sx) ** 2 + sa * sb * rho * x)
        self.points = (self - u).points


class P3SemiCon(DataErrors):

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            isData = False
            channel = 1
            for row in f:
                r = row.strip()  # remove trailing line break
                if isData:
                    if r == '<<END>>':
                        isData = False
                    else:
                        y = float(r)
                        self.addPoint(channel, y, 0, np.sqrt(y))
                        channel += 1
                else:
                    if r == '<<DATA>>':
                        isData = True


def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)
