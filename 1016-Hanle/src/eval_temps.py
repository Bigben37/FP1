#!/usr/bin/python2.7
from ROOT import TCanvas, TMultiGraph, TLegend, gPad

from data import DataErrors
from fitter import Fitter
from functions import setupROOT, loadCSVToList

from hanle import setMultiGraphTitle, TempToSeries, serieslabels, seriescolors, STEMP


def makeGraph(xlist, ylist, slist, xerror, yerror, xlabel, ylabel, name, fit=False, fitlabel=''):
    xmin = min(xlist)
    xmax = max(xlist)

    datas = dict()
    for x, y, s in zip(xlist, ylist, slist):
        if datas.has_key(s):
            datas[s].append((x, y, xerror, yerror))
        else:
            datas[s] = [(x, y, xerror, yerror)]

    c = TCanvas('c_%s' % name, '', 1280, 720)
    graphs = TMultiGraph()
    for s, datalist in datas.iteritems():
        data = DataErrors.fromLists(*zip(*datalist))
        g = data.makeGraph('g_%s_%d' % (name, s))
        g.SetMarkerColor(seriescolors[s])
        g.SetLineColor(seriescolors[s])
        graphs.Add(g)
    graphs.Draw('AP')
    gPad.Update()
    setMultiGraphTitle(graphs, xlabel, ylabel)

    if fit:
        fit = Fitter('fit_%s' % name, 'pol1(0)')
        fit.setParam(0, 'a')
        fit.setParam(1, 'b')
        fit.fit(graphs, xmin - 1, xmax + 1)
        fit.saveData('../calc/fit_%s.txt' % name, 'w')

    if fit:
        yheight = 0.3
    else:
        yheight = 0.15
    if ylist[0] < ylist[-1]:  # /
        l = TLegend(0.15, 0.85 - yheight, 0.4, 0.85)
    else:  # \
        l = TLegend(0.6, 0.85 - yheight, 0.85, 0.85)
    l.SetTextSize(0.03)
    for i, graph in enumerate(graphs.GetListOfGraphs()):
        l.AddEntry(graph, serieslabels[i], 'p')
    if fit:
        l.AddEntry(fit.function, 'Fit mit %s' % fitlabel, 'l')
        fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.3f', '%.3f')], chisquareformat='%.2f', advancedchi=True, units=['U', '#Omega'])
    l.Draw()

    c.Update()
    c.Print('../img/graph_%s.pdf' % name, 'pdf')

def main():
    SU = 0.2
    SI = 0.02

    datalist = loadCSVToList('../data/temps.txt')
    listT, listI, listU = zip(*datalist)
    listSeries = [TempToSeries(T) for T in listT]
    makeGraph(listI, listU, listSeries, SI, SU, 'Stromst#ddot{a}rke I / A', 'Spannung U / V', 'U-I', True, 'I(U) = a + b*U')
    makeGraph(listI, listT, listSeries, SI, STEMP, 'Stromst#ddot{a}rke I / A', 'Temperatur T / {}^{#circ} C', 'T-I')
    makeGraph(listU, listT, listSeries, SU, STEMP, 'Spannung U / V', 'Temperatur T / {}^{#circ} C', 'T-U')

if __name__ == "__main__":
    setupROOT()
    main()
