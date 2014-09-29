#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
import os
import numpy as np
from data import DataErrors
from szint import SzintData
from fitter import Fitter

def loadCSVToList(path, delimiter='\t'):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        data = []
        with open(p, 'r') as f:
            for line in f:
                data.append(list(map(lambda x: float(x), line.strip().split(delimiter))))  # remove \n, split by delimiter, convert to float
        return data

def evalAngles():
    # load data and set errors
    datalist = loadCSVToList('../data/angles.txt')
    l = len(datalist)
    data = DataErrors().fromLists(list(zip(*datalist)[0]), list(zip(*datalist)[1]), ex=[0.5] * l, ey=[0] * l)
    data.setYErrorFunc(lambda x: np.sqrt(x))
    
    #draw graph
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Winkel #alpha / #circ', 'Counts N')
    g.SetMarkerStyle(1)
    g.Draw('AP')
    
    #fit function
    fit = Fitter('f', '[0]+gaus(1)')
    fit.function.SetNpx(1000)  # for smoother curve
    fit.setParam(0, 'offset', 35)
    fit.setParam(1, 'ampl', 350)
    fit.setParam(2, 'theta', 180)
    fit.setParam(3, 'sigma', 20)
    fit.fit(g, 80, 280)
    fit.saveData('../calc/angles.txt', 'w')

    fit2 = Fitter('f', '[0]+1/2*[4]*(TMath::Erf(([1]+2*x-2*[2])/(2*sqrt(2)*[3]))+TMath::Erf(([1]-2*x+2*[2])/(2*sqrt(2)*[3])))')
    fit2.function.SetNpx(1000)  # for smoother curve
    fit2.function.SetLineColor(4)
    fit2.setParam(0, 'offset', 20)
    fit2.setParam(1, 'breite', 20)
    fit2.setParam(2, 'theta', 180)
    fit2.setParam(3, 'sigma', 5)
    fit2.setParam(4, 'amplitude', 350)
    fit2.fit(g, 80, 280, '+')
    fit2.saveData('../calc/angles_convolution.txt', 'w')
    
    l = TLegend(0.65, 0.55, 0.85, 0.85)
    l.AddEntry('g', 'Messwerte', 'p')
    l.AddEntry(fit.function, 'Fit mit Gaussverteilung', 'l')
    l.AddEntry(0, '#chi^2 / DoF = %.1f' % fit.getChisquareOverDoF(), '')
    l.AddEntry(0, '#alpha_{0,g} = (%.1f #pm %.1f) #circ' % (fit.params[2]['value'], fit.params[2]['error']), '')
    l.AddEntry(fit2.function, 'Fit mit Faltungsprodukt', 'l')
    l.AddEntry(0, '#chi^2 / DoF = %.1f' % fit2.getChisquareOverDoF(), '')
    l.AddEntry(0, '#alpha_{0,f} = (%.1f #pm %.1f) #circ' % (fit2.params[2]['value'], fit2.params[2]['error']), '')
    l.Draw()
    
    #print to file
    c.Update()
    c.Print('../img/angles.pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalAngles()

if __name__ == "__main__":
    main()