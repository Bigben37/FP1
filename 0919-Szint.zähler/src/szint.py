#!/usr/bin/python2.7
import os
import numpy as np
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there


class SzintData(DataErrors):

    def __init__(self):
        super(SzintData, self).__init__()
        self.time = 0
        self.timed = 0

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            lines = -1  # lines 1 and 2 are time information, line 3 starts with channel 1
            for row in f:
                if lines == -1:
                    self.time = float(row)
                elif lines == 0:
                    self.timed == float(row)
                else:
                    self.addPoint(lines, float(row), 0, np.sqrt(float(row)))
                lines += 1

    def subtractUnderground(self):
        u = SzintData.fromPath('../data/untergrund.TKA')
        u.convertToCountrate()
        self.points = (self - u).points

    def convertToCountrate(self):
        self.multiplyY(1. / self.time)

    def prepare(self):
        self.convertToCountrate()
        self.subtractUnderground()


def channelToEnergy(x, sx, gauge):
    """convert channel to energy with calculated energy gauge

    Arguments:
    x     -- channel
    sx    -- error of channel
    gauge -- fit parameter of energy-channel fit
    """
    # set params and erros of E = a + b*x + x*x^2
    a, sa = gauge[0]
    b, sb = gauge[1]
    c, sc = gauge[2]
    rhoab = gauge[3][0]
    rhoac = gauge[4][0]
    rhobc = gauge[5][0]
    # calculate energy and error
    E = a + b * x + c * (x ** 2)
    sE = np.sqrt(sa ** 2 + 2 * rhoab * sa * sb * x + (sb * x) ** 2 + 2 * rhoac * sa * sc * (x ** 2)
                 + 2 * rhobc * sb * sc * (x ** 3) + (sc ** 2) * (x ** 4) + (sx * (b + 2 * c * x)) * 2)
    return E, sE


def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)
