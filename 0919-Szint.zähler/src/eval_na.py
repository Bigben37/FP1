#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter
from txtfile import TxtFile


def evalNa():
    data = SzintData.fromPath('../data/na.TKA')
    data.prepare()

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMarkerStyle(1)
    g.SetMinimum(-0.01)
    g.GetXaxis().SetRangeUser(0, 8200)
    g.Draw('APX')

    fit = Fitter('f', 'pol1(0) + gaus(2)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'A', 0.05)
    fit.setParam(3, 'c', 1250)
    fit.setParam(4, 's', 50)
    fit.fit(g, 1200, 1390)
    fit.saveData('../calc/na_peak.txt', 'w')
    
    with TxtFile('../calc/energy_na.txt', 'w') as f:
        f.writeline('\t', '511', str(fit.params[3]['value']), str(fit.params[3]['error']))
    
    #TODO legend

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
