#!/usr/bin/python2.7
import numpy as np
from functions import setupROOT, loadCSVToList, avgerrors
from halbleiter import P2SemiCon
from ROOT import TCanvas, TLegend
from fitter import Fitter
from data import DataErrors
from txtfile import TxtFile


PRINTGRAPHS = False  # set False for quicker testing


def getParams():
    params = []
    params.append([[0.008, 0, 2.5e-8, 22e-6, 3e-6], 12e-6, 35e-6])
    params.append([[0.00675, 0, 6e-9, 20e-6, 2.5e-6], 10e-6, 32e-6])
    params.append([[0, 0, 9e-9, 17.5e-6, 2.5e-6], 13e-6, 22e-6])
    params.append([[0.0025, 0, 1e-8, 16e-6, 2.5e-6], 10e-6, 22e-6])
    params.append([[-0.003, 0, 2e-8, 14e-6, 2.5e-6], 8e-6, 20e-6])
    params.append([[0.003, 0, 2.5e-8, 12.5e-6, 2.5e-6], 6e-6, 20e-6])
    params.append([[-0.0005, 0, 4e-8, 10e-6, 2.5e-6], 5e-6, 17.5e-6])
    params.append([[-0.003, 0, 5e-8, 7.5e-6, 2.5e-6], 3e-6, 15e-6])
    params.append([[-0.001, 0, 6e-8, 6e-6, 2e-6], 3e-6, 9e-6])
    params.append([[-0.005, 0, 7e-8, 4e-6, 1.5e-6], 1e-6, 8e-6])
    params.append([[-0.0015, 0, 8e-8, 2.5e-6, 1e-6], 1e-6, 3.55e-6])
    return params


def getDistances():
    # load data
    f = lambda x: x[0]
    distances = loadCSVToList('../data/part2/length/lengths.txt')
    distances = map(f, distances)
    sd = 0.05
    return map(lambda x: (x, sd), distances)


def getByCloseX(data, x):
    for i in xrange(data.getLength() - 1):
        if data.points[i][0] <= x < data.points[i + 1][0]:
            return data.points[i]
    return data.points[data.getLength() - 1]


def evalDistance(n, params):
    xmin, xmax = params[1:]
    deltax = abs(xmax - xmin) * 0.1

    data = P2SemiCon.fromPath('../data/part2/length/ALL%04.d/F%04dCH1.CSV' % (n, n))
    g = data.makeGraph('g%d' % n, 'Zeit t / s', 'Spannung U / V')
    c = TCanvas('c%d' % n, '', 1280, 720)
    g.SetMarkerStyle(1)
    g.GetXaxis().SetRangeUser(xmin - deltax, xmax + deltax)
    closex = min(getByCloseX(data, xmin)[1], getByCloseX(data, xmax)[1])
    if closex > 0:
        ymin = closex * 0.95
    else:
        ymin = closex * 1.1
    g.SetMinimum(ymin)
    g.GetYaxis().SetTitleOffset(1.2)
    g.Draw('APX')

    fit = Fitter('f', 'pol1(0) + 1/(sqrt(2*pi*[4]^2))*gaus(2)')
    fit.function.SetNpx(1000)
    paramname = ['a', 'b', 'A', 't_{c}', '#sigma']
    for i, param in enumerate(params[0]):
        fit.setParam(i, paramname[i], param)
    fit.fit(g, xmin, xmax)
    fit.saveData('../calc/part2/dist%02d.txt' % n, 'w')

    l = TLegend(0.625, 0.6, 0.99, 0.99)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit U(t) = a + b*t + #frac{A}{#sqrt{2#pi*#sigma^{2}}} e^{- #frac{1}{2} (#frac{t - t_{c}}{#sigma})^{2}}', 'l')
    l.AddEntry(0, '', '')
    fit.addParamsToLegend(l, [('%.2e', '%.2e')] * len(params[0]), chisquareformat='%.2f')
    l.Draw()

    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/dist%02d.pdf' % n, 'pdf')

    return data, fit.params, fit.getCorrMatrix(), params[1], params[2]


def plotDistances(graphs, distances):
    c = TCanvas('cL', '', 1280, 720)
    l = TLegend(0.65, 0.3, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(0, 'Abst#ddot{a}nde d / mm', '')
    first = True
    for i, g in enumerate(graphs):
        g.SetMarkerStyle(1)
        g.SetMarkerColor(int(round(51 + (100. - 51) / 11 * i)))
        g.GetXaxis().SetRangeUser(1e-6, 26e-6)
        if first:
            g.Draw('APX')
            g.SetMaximum(50e-3)
            g.SetMinimum(0)
            first = False
        else:
            g.Draw('PX')
        l.AddEntry(g, '%.2f' % distances[i][0], 'p')
    l.Draw()
    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/distances.pdf', 'pdf')


def fitXc(dists, times):
    listx, listsx = zip(*times)
    listy, listsy = zip(*dists)
    data = DataErrors.fromLists(listx, listy, listsx, listsy)

    c = TCanvas('cXc', '', 1280, 720)
    g = data.makeGraph('xc', 'Zeit t / s', 'x_{c} / mm')
    g.SetLineWidth(0)
    g.Draw('AP')

    fit = Fitter('fitXc', 'pol1(0)')
    fit.setParam(0, 'x_{0}', 1)
    fit.setParam(1, 'm', 0.5e-6)
    fit.fit(g, 1e-6, 23e-6)
    fit.saveData('../calc/part2/dist_fit_xc.txt')

    l = TLegend(0.15, 0.625, 0.4, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry('xc', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit x_{c}(t) = x_{0}+m*t', 'l')
    l.AddEntry(0, '', '')
    fit.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.2e', '%.2e')], chisquareformat='%.2f')
    l.Draw()

    if PRINTGRAPHS or True:
        c.Update()
        c.Print('../img/part2/dist_fitXc.pdf', 'pdf')

    # calculate mu
    m, sm = fit.params[1]['value'], fit.params[1]['error']
    U, sU = 48.8, P2SemiCon.UERROR
    l = 30
    mu = m * l / U / 100  # /100 -> from mm in cm
    smu = mu * np.sqrt((sm / m) ** 2 + (sU / U) ** 2)
    with TxtFile('../calc/part2/dist_mu.txt', 'w') as f:
        f.writeline('\t', str(mu), str(smu))

    return mu, smu


def fitA(amps, times):
    listx, listsx = zip(*times)
    listy, listsy = zip(*amps)
    slaser_rel = 0.05
    listsy = list(listsy)
    for i, y in enumerate(listy):
        listsy[i] = y * np.sqrt(listsy[i] ** 2 + slaser_rel ** 2)
    
    data = DataErrors.fromLists(listx, listy, listsx, listsy)

    c = TCanvas('cA', '', 1280, 720)
    g = data.makeGraph('A', 'Zeit t / s', 'Amplitude A / V')
    g.Draw('AP')

    fit = Fitter('A', '[0]*exp(-(x)/[1])+[2]')
    fit.function.SetNpx(1000)
    fit.setParam(0, 'C', 5e-8)
    fit.setParam(1, '#tau_{n}', 45e-6)
    fit.setParam(2, 'a', 0)
    fit.fit(g, 1e-6, 23e-6)
    fit.saveData('../calc/part2/dist_fit_A.txt')

    l = TLegend(0.575, 0.5, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry('A', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit A(t) = C*e^{- #frac{t}{#tau_{n}}} + a', 'l')
    l.AddEntry(0, 'Parameter:', '')
    fit.addParamsToLegend(l, [('%.2e', '%.1e'), ('%.2e', '%.1e'), ('%.2e', '%.1e')], chisquareformat='%.2f')
    l.Draw()

    if PRINTGRAPHS or True:
        c.Update()
        c.Print('../img/part2/dist_fitA.pdf', 'pdf')


def fitSigma(sigs, times):
    listx, listsx = zip(*times)
    listy, listsy = zip(*sigs)
    listy = map(abs, listy)   # fits can yield negative sigma, because it only occurse to
    data = DataErrors.fromLists(listx, listy, listsx, listsy)

    c = TCanvas('cSigma', '', 1280, 720)
    g = data.makeGraph('Sigma', 'Zeit t / s', 'Standardabweichung #sigma / m')
    g.Draw('AP')

    fit = Fitter('fitS', 'sqrt(2*[0]*(x + [1]))')
    fit.setParam(0, 'D_{n}', 100)
    fit.setParam(1, 'x0', 0)
    fit.fit(g, 1e-6, 21e-6)
    fit.saveData('../calc/part2/dist_fit_sigma.txt')

    l = TLegend(0.15, 0.65, 0.4, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry('Sigma', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit #simga(t) = #sqrt{2*D_{n}*t}', 'l')
    fit.addParamsToLegend(l, [('%.1f', '%.1f'), ('%.2e', '%.2e')], chisquareformat='%.2f')
    l.Draw()

    if PRINTGRAPHS or True:
        c.Update()
        c.Print('../img/part2/dist_fitSigma.pdf', 'pdf')


def evalDistances():
    params = getParams()
    distances = getDistances()
    fittedData = []
    for i, param in enumerate(params):
        fittedData.append(evalDistance(i, param))

    graphs = []  # list of graphs
    amps = []  # amplitudes
    times = []   # times
    sigs = []  # sigmas
    for data, param, corrMatrix, xmin, xmax in fittedData:
        # get data for further fits
        amps.append((param[2]['value'], param[2]['error']))
        times.append((param[3]['value'], param[3]['error']))
        sigs.append((abs(param[4]['value']), param[4]['error']))  # abs for negative sigmas

        # for plotting all data in one graph
        data.filterX(xmin, xmax)
        data.subtractUnderground(param[0]['value'], param[1]['value'], param[0]['error'], param[1]['error'], corrMatrix[0][1])
        data.addPoint(-1e-6, 0, 0, 0)  # otherwise SetRangeUser() doesn't work
        data.addPoint(30e-6, 0, 0, 0)  # otherwise SetRangeUser() doesn't work
        graphs.append(data.makeGraph('g', 'Zeit t / s', 'Spannung U / V'))
    plotDistances(graphs, distances)

    # fit params of gauss
    mu, smu = fitXc(distances, times)  # in cm^2 / s
    fitA(amps, times)
    E = 48.8 / 3  # in V / cm
    sigs = map(lambda x: (x[0] * mu * E, x[0] * mu * E * np.sqrt((x[1] / x[0]) ** 2 + (smu / mu) ** 2)), sigs)
    fitSigma(sigs, times)


def main():
    setupROOT()
    evalDistances()


if __name__ == "__main__":
    main()
