#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend, TLine
from farpock import FaraData
from fitter import Fitter
from txtfile import TxtFile


def evalFaraday():
    data = FaraData.fromPath('../data/fara_data.txt')

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Strom I / A', 'Winkel #alpha / #circ')
    g.GetXaxis().SetRangeUser(-6, 6)
    g.SetMinimum(-15)
    g.SetMaximum(15)
    g.Draw('AP')

    vline = TLine(0, -15, 0, 15)
    vline.Draw()
    hline = TLine(-6, 0, 6, 0)
    hline.Draw()

    fit = Fitter('f', 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 2)
    fit.fit(g, -5.5, 5.5)
    fit.saveData('../calc/faraday.txt', 'w')

    l = TLegend(0.15, 0.65, 0.35, 0.85)
    l.AddEntry('g', 'Messwerte', 'p')
    l.AddEntry(fit.function, 'Fit mit y = a + b*x', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'a = %.2f #pm %.2f' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.AddEntry(0, 'b = %.3f #pm %.3f' % (fit.params[1]['value'], fit.params[1]['error']), '')
    l.Draw()

    c.Update()
    c.Print('../img/faraday.pdf', 'pdf')

    b = (fit.params[1]['value'], fit.params[1]['error'])
    c = 2554.85
    N = 3600
    v = map(lambda x: x / c, b)  # verdet constant
    oe = 60 * 79.58 / 100  # factor for min/(Oe*cm)
    voe = map(lambda x: x * oe, v)  # verdet in min/(Oe*cm)
    vi = map(lambda x: x / N, b)  # ideal 
    vioe = map(lambda x: x * oe, vi)
    with TxtFile('../calc/faraday_verdet.txt', 'w') as f:
        f.writeline('\t', *map(str, v))
        f.writeline('\t', *map(str, voe))
        f.writeline('\t', *map(str, vi))
        f.writeline('\t', *map(str, vioe))


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalFaraday()

if __name__ == "__main__":
    main()
