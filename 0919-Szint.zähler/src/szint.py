#!/usr/bin/python2.7
import os
import numpy as np
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there


class SzintData(DataErrors):
    BINERROR = 1

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
                else:                                                   # TODO wieviel binerror?
                    self.addPoint(lines, float(row), 0, self.BINERROR)  # TODO poisson error auf y-werte?
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


def channelToEnergy(c, sc, gauge):
    """convert channel to energy with calculated energy gauge

    Arguments:
    c     -- channel
    sc    -- error of channel
    gauge -- fit parameter of energy-channel fit
    """
    # set params and erros of E = a + b*c
    a, sa = gauge[0]
    b, sb = gauge[1]
    rho = gauge[2][0]
    # calculate energy and error
    E = a + b * c
    sE = np.sqrt(sa ** 2 + c * rho * sa * sb + (c * sb) ** 2 + (b * sc) ** 2)

    return E, sE
