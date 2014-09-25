#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter
from txtfile import TxtFile


def evalCo():
    data = SzintData.fromPath('../data/co.TKA')
    data.prepare()

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMarkerStyle(1)
    g.SetMinimum(-0.01)
    g.GetXaxis().SetRangeUser(0, 8200)
    g.Draw('AP')

    fit = Fitter('f', 'pol1(0) + gaus(2) + gaus(5)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'A1', 0.1)
    fit.setParam(3, 'c1', 2800)
    fit.setParam(4, 's1', 50)
    fit.setParam(5, 'A2', 0.1)
    fit.setParam(6, 'c2', 3250)
    fit.setParam(7, 's2', 75)
    fit.fit(g, 2650, 3500)
    fit.saveData('../calc/co_peaks.txt', 'w')
    
    with TxtFile('../calc/energy_co.txt', 'w') as f:
        f.writeline('\t', '1172', str(fit.params[3]['value']), str(fit.params[3]['error']))
        f.writeline('\t', '1332', str(fit.params[6]['value']), str(fit.params[6]['error']))
    
    # TODO legend

    c.Update()
    c.Print('../img/co_peaks.pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalCo()

if __name__ == "__main__":
    main()
