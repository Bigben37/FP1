#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData, prepareGraph
from fitter import Fitter
from txtfile import TxtFile


def evalCo():
    data = SzintData.fromPath('../data/co.TKA')
    data.prepare()

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    prepareGraph(g)
    g.SetMinimum(-0.01)
    g.GetXaxis().SetRangeUser(0, 8200)
    g.Draw('APX')

    c.Update()
    c.Print('../img/co_spectrum.pdf')

    fit = Fitter('f', 'pol1(0) + gaus(2) + gaus(5)')
    fit.function.SetLineWidth(2)
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

    l = TLegend(0.635, 0.62, 0.87, 0.87)
    l.AddEntry('g', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit y = a + b*x + gaus(x; A1, c1, s1)', 'l')
    l.AddEntry(fit.function, '                  + gaus(x; A2, c2, s2)', '')
    l.AddEntry(0, '#chi^{2} / DoF : %f' % fit.getChisquareOverDoF(), '')
    l.AddEntry(0, 'Peaks:', '')
    l.AddEntry(0, 'c1 = %.2f #pm %.2f' % (fit.params[3]['value'], fit.params[3]['error']), '')
    l.AddEntry(0, 'c2 = %.2f #pm %.2f' % (fit.params[6]['value'], fit.params[6]['error']), '')
    l.Draw()

    g.GetXaxis().SetRangeUser(2400, 3800)
    g.Draw('P')
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
