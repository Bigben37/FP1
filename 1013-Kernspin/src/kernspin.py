from data import Data  # make sure to add ../lib to your project path or copy file from there
import numpy as np
import os

ERRORS = {'B': 1, 'nu': 0.005, 'x': 0.5, 'I': 0.01}


class NMRData(Data):

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            first = True
            for row in f:
                if first:
                    first = False
                else:
                    x, y = row.strip().split(',')
                    self.addPoint(float(x), float(y))
