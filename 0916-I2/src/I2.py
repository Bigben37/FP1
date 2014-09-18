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
        """finds extrema in data points by comparing near by values
        
        Arguments:
        steps   -- number of comparisons to right and left side
        xstart  -- start of x interval in which extrema are analyzed
        xend    -- end of x interval in which extrema are anayzed
        minimum -- if true searches for minima, if false searches for maxima (default = True)
        """
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
    
    def calcVacuumLambda(self):
        """changes wavelength to vacuum wavelength. The refraction index depends on wavelength, its approximated by a polynomial 
        or first order (n(s) = a + b*s, where x is wavelength)."""
        a = 1.00028678401
        b = -1.60115242176e-08
        for i in range(self.getLength()):
            points[i][0] *= a + b*points[i][0]