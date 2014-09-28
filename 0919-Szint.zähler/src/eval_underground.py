#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData, channelToEnergy
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
    g = data.makeGraph('', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMarkerStyle(1)
    g.Draw('APX')

    # fit
    fit = Fitter('f', 'pol1(0) + gaus(2)')
    fit.setParam(0, 'a', 2e-3)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'A1', 1e-2)
    fit.setParam(3, 'c1', 3500)
    fit.setParam(4, 's1', 200)
    fit.fit(g, 3250, 4050)
    fit.saveData('../calc/underground_peak.txt', 'w')

    p, pc = fit.params[3]['value'], fit.params[4]['error']
    E, sE = channelToEnergy(p, pc, gauge)
    with TxtFile('../calc/underground_peak_energy.txt', 'w') as f:
        f.writeline('\t', *map(lambda x: str(x), (p, pc, E, sE)))

    # TODO Legend

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
