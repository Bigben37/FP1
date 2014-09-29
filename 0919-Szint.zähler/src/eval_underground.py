#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData, channelToEnergy, prepareGraph
from fitter import Fitter
import functions as funcs
from txtfile import TxtFile


def evalUnderground():
    # load data
    data = SzintData.fromPath('../data/untergrund.TKA')
    data.convertToCountrate()
    gauge = funcs.loadCSVToList('../calc/energy_gauge_raw.txt')

    # make canvas and graph
    c = TCanvas('c', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 8200)
    g.Draw('APX')
    
    c.Update()
    c.Print('../img/underground_spectrum.pdf')

    # fit
    fit = Fitter('f', 'pol1(0) + gaus(2)')
    fit.setParam(0, 'a', 2e-3)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'A1', 1e-2)
    fit.setParam(3, 'c1', 3500)
    fit.setParam(4, 's1', 200)
    fit.fit(g, 3250, 4050)
    fit.saveData('../calc/underground_peak.txt', 'w')

    p, sp = fit.params[3]['value'], fit.params[3]['error']
    E, sE = channelToEnergy(p, sp, gauge)
    with TxtFile('../calc/underground_peak_energy.txt', 'w') as f:
        f.writeline('\t', *map(lambda x: str(x), (p, sp, E, sE)))

    l = TLegend(0.6, 0.7, 0.85, 0.85)
    l.AddEntry('g', 'Messwerte', 'p')
    l.AddEntry(fit.function, 'Fit mit y = a + b*x + gaus(x; A, c, s)', 'l')
    l.AddEntry(0, 'Peak: ', '')
    l.AddEntry(0, 'c1 = %.2f #pm %.2f' % (p, sp), '')
    l.Draw()

    c.SetLogy(False)
    g.GetXaxis().SetRangeUser(3200, 4100)
    g.SetMinimum(0.00025)
    g.SetMaximum(0.016)
    g.Draw('P')
    c.Update()
    c.Print('../img/underground_peaks.pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalUnderground()

if __name__ == "__main__":
    main()
