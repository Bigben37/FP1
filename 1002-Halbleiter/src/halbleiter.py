#!/usr/bin/python2.7
from data import DataErrors
import os, csv

class P2SemiCon(DataErrors):
    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                x, y = row[3:5]
                self.addPoint(float(x), float(y), 0, 0)