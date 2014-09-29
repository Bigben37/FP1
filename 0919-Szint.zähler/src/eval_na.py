#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData, prepareGraph
from fitter import Fitter
from txtfile import TxtFile


def evalNa():
    data = SzintData.fromPath('../data/na.TKA')
    data.prepare()

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    prepareGraph(g)
    g.SetMinimum(-0.01)
    g.GetXaxis().SetRangeUser(0, 8200)
    g.Draw('APX')

    c.Update()
    c.Print('../img/na_spectrum.pdf')

    fit1 = Fitter('f', 'pol1(0) + gaus(2)')
    fit1.function.SetLineWidth(2)
    fit1.setParam(0, 'a', 0)
    fit1.setParam(1, 'b', 0)
    fit1.setParam(2, 'A', 0.05)
    fit1.setParam(3, 'c', 1250)
    fit1.setParam(4, 's', 50)
    fit1.fit(g, 1200, 1390)
    fit1.saveData('../calc/na_peak1.txt', 'w')

    fit2 = Fitter('f', 'pol1(0) + gaus(2)')
    fit2.function.SetLineWidth(2)
    fit2.function.SetLineColor(4)
    fit2.setParam(0, 'a', 0)
    fit2.setParam(1, 'b', 0)
    fit2.setParam(2, 'A', 0.01)
    fit2.setParam(3, 'c', 3100)
    fit2.setParam(4, 's', 50)
    fit2.fit(g, 3000, 3300, '+')
    fit2.saveData('../calc/na_peak2.txt', 'w')

    with TxtFile('../calc/energy_na.txt', 'w') as f:
        f.writeline('\t', '511', str(fit1.params[3]['value']), str(fit1.params[3]['error']))
        f.writeline('\t', '1274', str(fit2.params[3]['value']), str(fit2.params[3]['error']))

    l = TLegend(0.635, 0.62, 0.87, 0.87)
    l.AddEntry('g', 'Messung', 'p')
    l.AddEntry(fit1.function, 'Fit des ersten Peaks', 'l')
    l.AddEntry(0, 'y = a1 + b1*x + gaus(x; A1, c1, s1)', '')
    l.AddEntry(fit2.function, 'Fit des zweiten Peaks', 'l')
    l.AddEntry(0, 'y = a2 + b2*x + gaus(x; A2, c2, s2)', '')
    l.AddEntry(0, 'Peaks:', '')
    l.AddEntry(0, 'c = %.2f #pm %.2f' % (fit1.params[3]['value'], fit1.params[3]['error']), '')
    l.AddEntry(0, 'c = %.2f #pm %.2f' % (fit2.params[3]['value'], fit2.params[3]['error']), '')
    l.Draw()

    g.GetXaxis().SetRangeUser(1000, 3600)
    g.SetMaximum(0.07)
    g.Draw('P')
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
