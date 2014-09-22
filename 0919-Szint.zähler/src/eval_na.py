#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter

def evalNa():
    data = SzintData.fromPath('../data/na.TKA')
    # TOD underground
    c = TCanvas('c', '', 1280, 720)
    #c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('AP')
    
    fit = Fitter('f', 'pol1(0) + gaus(2)')
    fit.setParam(0, 'a', 60)
    fit.setParam(1, 'b', -0.05)
    fit.setParam(2, 'A', 100)
    fit.setParam(3, 'c', 1300)
    fit.setParam(4, 's', 50)
    fit.fit(g, 1200, 1400)
    fit.saveData('../calc/na_peak.txt', 'w')
    
    c.Update()
    c.Print('../img/na_peaks.pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalNa()

if __name__ == "__main__":
    main()