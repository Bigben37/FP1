#!/usr/bin/python2.7
from functions import setupROOT, loadCSVToList  # make sure to add ../lib to your project path or copy file from there
from data import DataErrors
from ROOT import TCanvas, TLegend
from txtfile import TxtFile
from fitter import Fitter
import numpy as np

def calcGyro(nu, snu, B, sB):
    B /= 1000  # mT -> T
    sB /= 1000  #mT -> T
    gyro = 2 * np.pi * nu / B
    sgyro = gyro * np.sqrt((snu / nu) ** 2 + (sB / B) ** 2)
    return gyro, sgyro

def main():
    snu = 0  # TODO get error
    sB = 0  # TODO get error
    files = ['H', 'Glycol']
    for file in files:
        datalist = loadCSVToList('../data/03-%s.txt' % file)
        if len(datalist) == 1:
            with TxtFile('../calc/gyro-%s.txt' % file, 'w') as f:
                B, nu = datalist[0]
                f.writeline('\t', *map(str, calcGyro(nu, snu, B, sB)))
        else:
            x, y = zip(*datalist)
            sx = [sB] * len(x)
            sy = [snu] * len(y)
            data = DataErrors.fromLists(x, y, sx, sy)
            c = TCanvas('c%s' % file, '', 1280, 720)
            g = data.makeGraph('g%s' % file, 'Magnetfeld B / mT', 'Resonanzfrequenz #nu / MHz')
            g.Draw('AP')
            
            fit = Fitter('fit%s' % file, 'pol1(0)')
            fit.setParam(0, 'a', 0)
            fit.setParam(1, 'b', 0.002)
            fit.fit(g, datalist[0][0] * 0.95, datalist[-1][0] * 1.05)
            fit.saveData('../calc/fit-%s.txt' % file, 'w')
            
            l = TLegend(0.15, 0.65, 0.45, 0.85)
            l.SetTextSize(0.03)
            l.AddEntry(g, 'Messdaten', 'p')
            l.AddEntry(fit.function, 'Fit mit ', 'l')
            fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.4f', '%.4f')])
            l.Draw()
            
            gyro = 2 * np.pi * fit.params[1]['value'] * 1000
            sgyro = 2 * np.pi * fit.params[1]['error'] * 1000
            with TxtFile('../calc/gyro-%s.txt' % file, 'w') as f:
                f.writeline('\t', str(gyro), str(sgyro))
            
            c.Update()
            c.Print('../img/03-%s.pdf' % file, 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()