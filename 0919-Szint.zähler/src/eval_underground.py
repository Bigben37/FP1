#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter


def evalUnderground():
    data = SzintData.fromPath('../data/untergrund.TKA')
    data.convertToCountrate()

    c = TCanvas('c', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('APX')

    fit = Fitter('f', 'pol1(0) + gaus(2)')
    fit.setParam(0, 'a', 2e-3)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'A1', 1e-2)
    fit.setParam(3, 'c1', 3500)
    fit.setParam(4, 's1', 200)
    fit.fit(g, 3250, 4050)
    fit.saveData('../calc/underground_peak.txt', 'w')
    
    #TODO Legend

    c.Update()
    c.Print('../img/underground.pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalUnderground()

if __name__ == "__main__":
    main()
