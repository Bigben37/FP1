#!/usr/bin/python2.7
import csv
import os
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there
                
class LHWZData(DataErrors):
    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                xi, yi = row
                self.addPoint(float(xi.replace(',', '.')), float(yi.replace(',', '.')), 0, 0)