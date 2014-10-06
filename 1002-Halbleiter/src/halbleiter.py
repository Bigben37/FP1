#!/usr/bin/python2.7
from data import DataErrors
import os
import csv
import numpy as np


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
                    