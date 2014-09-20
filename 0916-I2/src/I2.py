#!/usr/bin/python2.7
import csv
import os
import numpy as np
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there
                
class I2Data(DataErrors):
    ERRORBIN = 0.097
    
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
    
    def useEnergyGauge(self):
        a  = 0.905359171563
        sa = 0.383787495854
        b  = 0.998715697202
        sb = 0.00071189084508
        sl = I2Data.ERRORBIN
        for i in range(self.getLength()):
            l = self.points[i][0]
            self.points[i] = (a + b*l, self.points[i][1], np.sqrt(sa**2 + (l*sb)**2 + (b*sl)**2), 0) 
    
    def calcVacuumLambda(self):
        """changes wavelength to vacuum wavelength. The refraction index depends on wavelength, its approximated by a polynomial 
        or first order (n(x) = a + b*x, where x is wavelength)."""
        a  = 1.00028678401
        sa = 8.45822036344e-07
        b  = -1.60115242176e-08
        sb = 1.44700016609e-09
        sl = I2Data.ERRORBIN
        for i in range(self.getLength()):
            l = self.points[i][0]
            self.points[i] = (l*(a + b*l), self.points[i][1], np.sqrt((l * sa)**2 + (l**2 * sb)**2 + ((a + 2 * b * l) * sl)**2), 0) 
           