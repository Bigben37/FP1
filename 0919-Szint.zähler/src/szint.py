#!/usr/bin/python2.7
import os
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
            lines = -1
            for row in f:
                if lines == -1:
                    self.time = float(row)
                elif lines == 0:
                    self.timed == float(row)
                else:
                    self.addPoint(lines, float(row) , 0, 0)
                lines += 1