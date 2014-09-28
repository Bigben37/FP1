#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter
from txtfile import TxtFile


def evalEu():
    data = SzintData.fromPath('../data/eu.TKA')
    data.prepare()

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMarkerStyle(1)
    g.GetXaxis().SetRangeUser(0, 4000)
    g.Draw('APX')
    
    fit1 = Fitter('f1', 'pol1(0)+gaus(2)')
    fit1.setParam(0, 'a', 0.5)
    fit1.setParam(1, 'b', 0)
    fit1.setParam(2, 'A', 2.5)
    fit1.setParam(3, 'c', 350)
    fit1.setParam(4, 's', 50)
    fit1.fit(g, 300, 400)
    fit1.saveData('../calc/eu_peak1.txt', 'w')
    
    fit2 = Fitter('f2', 'pol1(0)+gaus(2)')
    fit2.function.SetLineColor(4)
    fit2.setParam(0, 'a', 0.5)
    fit2.setParam(1, 'b', 0)
    fit2.setParam(2, 'A', 1.5)
    fit2.setParam(3, 'c', 900)
    fit2.setParam(4, 's', 75)
    fit2.fit(g, 800, 1000, '+')
    fit2.saveData('../calc/eu_peak2.txt', 'w')
    
    with TxtFile('../calc/energy_eu.txt', 'w') as f:
        f.writeline('\t', '122', str(fit1.params[3]['value']), str(fit1.params[3]['error']))
        f.writeline('\t', '344', str(fit2.params[3]['value']), str(fit2.params[3]['error']))
    
    #TODO legend
    
    c.Update()
    c.Print('../img/eu_peaks.pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalEu()

if __name__ == "__main__":
    main()
