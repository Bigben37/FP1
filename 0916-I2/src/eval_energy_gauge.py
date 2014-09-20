#!/usr/bin/python2.7
import os
from ROOT import gROOT, gStyle, TCanvas, TLegend
from I2 import I2Data
from data import DataErrors
from fitter import Fitter

def readFileToList(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        lines = []
        with open(p, 'r') as f:
            for line in f:
                lines.append(float(line))
        return lines

def energyGauge():
    dataList = readFileToList('../calc/hg_lines.txt')
    dataList += readFileToList('../calc/na_lines.txt')
    litVals = readFileToList('../data/hg_litvals.txt')
    litVals += readFileToList('../data/na_litvals.txt')
    data = DataErrors()
    for val, litval in zip(dataList, litVals):
        data.addPoint(val, litval, I2Data.ERRORBIN, 0)
        
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'measured wavelength / nm', 'literature value / nm')
    g.Draw('AP')
    
    fit = Fitter('f', '[0]+[1]*x')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 1)
    fit.fit(g, 420, 600)
    fit.saveData('../calc/fit_energy_gauge.txt', 'w')
    
    l = TLegend(0.15, 0.6, 0.5, 0.85)
    l.AddEntry(fit.function, 'y = a + b*x', 'l')
    fit.addParamsToLegend(l)
    l.SetTextSize(0.03)
    l.Draw()
    
    c.Update()
    c.Print('../img/energy_gauge.pdf', 'pdf')

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    energyGauge()

if __name__ == "__main__":
    main()