#!/usr/bin/python2.7
import csv
import os
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there
                
class I2Data(DataErrors):
    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) == 2:
                    xi, yi = row
                    self.addPoint(float(xi.replace(',', '.')), float(yi.replace(',', '.')), 0, 0)
                    
    def findExtrema(self, steps, xstart, xend, minimum=True):
        m = 1 if minimum else -1  # modifier for maxima/minimia
        data = I2Data()
        for i in range(steps, self.getLength() - steps):
            if xstart <= self.points[i][0]  <= xend:
                passed = True
                for j in range(-steps, steps):
                    passed = passed and (m*self.points[i][1] <= m*self.points[i+j][1])
                if passed:
                    data.addPoint(*self.points[i])
        return data