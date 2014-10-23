#!/usr/bin/python2.7
from functions import setupROOT, loadCSVToList
from data import DataErrors
from ROOT import TCanvas, TLegend
from fitter import Fitter
from txtfile import TxtFile
import numpy as np

ST = 2
serieslabels = {0: 'Tag 1, abk#ddot{u}hlen', 1: 'Tag 2, abk#ddot{u}hlen', 2: 'Tag 2, aufw#ddot{a}rmen'}


def TempToSeries(T):
    series = [[23, 19, 14], [7, 5, 0, -1, -3, -4, -7, -8], [3, 10]]
    for i, s in enumerate(series):
        if T in s:
            return i
    return None


def TempToPressure(T):
    T2 = 273.15 + T
    pc = 167000000.
    Tc = 1764.
    Tr = 1. - T2 / Tc
    a1 = -4.57618368
    a2 = -1.40726277
    a3 = 2.36263541
    a4 = -31.0889985
    a5 = 58.0183959
    a6 = -27.6304546
    return 1000 * pc * np.exp((Tc / T2) * (a1 * Tr + a2 * Tr ** 1.89 + a3 * Tr ** 2 + a4 * Tr ** 8 +
                                           a5 * Tr ** 8.5 + a6 * Tr ** 9))


def printOverview(datas, phi, mintau, maxtau):
    # make graphs
    c = TCanvas('c_%d' % phi)
    colors = [1, 4, 5]
    graphs = []
    for s, datalist in datas.iteritems():
        data = DataErrors.fromLists(*zip(*datalist))
        g = data.makeGraph('g_%d_%d' % (phi, s), 'Druck p / mPa', '#tau / ns')
        g.SetMarkerColor(colors[s])
        g.SetLineColor(colors[s])
        g.SetMinimum(mintau - 5)
        g.SetMaximum(maxtau + 5)
        g.GetXaxis().SetLimits(0, 230)
        graphs.append(g)

    for i in [1, 0, 2]:
        if i == 1:
            graphs[i].Draw('AP')
        else:
            graphs[i].Draw('P')
    
    l = TLegend(0.15, 0.7, 0.4, 0.85)
    for i, graph in enumerate(graphs):
        l.AddEntry(graph, serieslabels[i], 'p')
    l.Draw()

    c.Update()
    c.Print('../img/taus_%02d.pdf' % phi, 'pdf')


def makeFit(datalist, phi, name=''):
    data = DataErrors.fromLists(*zip(*datalist))
    c = TCanvas('c_fit_%d' % phi, '', 1280, 720)
    g = data.makeGraph('g_fit_%d' % phi, 'Druck p / mPa', '#tau / ns')
    g.GetXaxis().SetLimits(0, max(data.getX()) * 1.1)
    g.Draw('AP')

    fit = Fitter('fit_%d' % phi, 'pol1(0)')
    fit.setParam(0, '#tau_{0}', 119)
    fit.setParam(1, 'm', 0.5)
    fit.fit(g, 0, 225, 'M')
    fit.saveData('../calc/fit_tau_%02d' % phi, 'w')

    l = TLegend(0.55, 0.15, 0.85, 0.4)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Lebensdauern (aus Fits)', 'p')
    l.AddEntry(fit.function, 'Fit mit #tau(p) = #tau_{0} + m * p', 'l')
    fit.addParamsToLegend(l, [('%.1f', '%.1f'), ('%.2f', '%.2f')], chisquareformat='%.2f', advancedchi=True, units=['ns', 'ns / mPa'])
    l.Draw()
    
    g.SetMinimum(min(fit.params[0]['value'], min(data.getY())*0.975))

    c.Update()
    c.Print('../img/taus_fit_%02d%s.pdf' % (phi, name), 'pdf')


def main():
    phis = [0, 45, 90]
    for phi in phis:
        # read data
        datalist = loadCSVToList('../calc/taus_%02d.txt' % phi)
        datas = {0: [], 1: [], 2: []}
        mintau = min(zip(*datalist)[1])
        maxtau = max(zip(*datalist)[1])
        for T, tau, stau in datalist:
            p = TempToPressure(T)
            sp = p * ST / (T + 273.15)
            datas[TempToSeries(T)].append((p, tau, sp, stau))  # sort in right series list

        printOverview(datas, phi, mintau, maxtau)
        makeFit(datas[0] + datas[1] + datas[2], phi, '_total')
        makeFit(datas[1], phi, '_partial')
        makeFit(datas[1] + datas[2], phi, '_day2')


if __name__ == '__main__':
    setupROOT()
    main()
