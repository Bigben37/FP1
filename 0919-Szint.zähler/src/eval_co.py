#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter

def evalNa():
    data = SzintData.fromPath('../data/co.TKA')
    # TODO underground
    c = TCanvas('c', '', 1280, 720)
    #c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('AP')
    
    fit = Fitter('f', 'pol1(0) + gaus(2) + gaus(5)')
    fit.setParam(0, 'a', 40)
    fit.setParam(1, 'b', -0.05)
    fit.setParam(2, 'A1', 250)
    fit.setParam(3, 'c1', 2900)
    fit.setParam(4, 's1', 50)
    fit.setParam(5, 'A2', 200)
    fit.setParam(6, 'c2', 3250)
    fit.setParam(7, 's2', 75)
    fit.fit(g, 2600, 3500)
    fit.saveData('../calc/co_peaks.txt', 'w')
    
    c.Update()
    c.Print('../img/co_peaks.pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalNa()

if __name__ == "__main__":
    main()