#!/usr/bin/python2.7
import numpy as np
from functions import setupROOT, loadCSVToList, avgerrors
from halbleiter import P2SemiCon
from ROOT import TCanvas, TLegend
from fitter import Fitter
from numpy import append
from data import DataErrors
from txtfile import TxtFile


PRINTGRAPHS = True  # set False for quicker testing


def getDistanceParams():
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
    sd = 0.005
    return map(lambda x: (x,sd), distances)


def evalDistance(n, params):
    data = P2SemiCon.fromPath('../data/part2/length/ALL%04.d/F%04dCH1.CSV' % (n, n))
    g = data.makeGraph()
    c = TCanvas('c%d' % n, '', 1280, 720)
    g.SetMarkerStyle(1)
    g.Draw('AP')

    fit = Fitter('f', 'pol1(0) + 1/(sqrt(2*pi*[4]^2))*gaus(2)')
    paramname = ['a', 'b', 'A', 'tm', 's']
    for i, param in enumerate(params[0]):
        fit.setParam(i, paramname[i], param)
    fit.fit(g, params[1], params[2])
    
    l = TLegend(0.15, 0.7, 0.3, 0.85)
    l.AddEntry(g, 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit Gausskurve', 'l')
    l.Draw()

    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/dist%02d.pdf' % n, 'pdf')

    return data, fit.params, fit.getCorrMatrix(), params[1], params[2]


def plotDistances(graphs, distances):
    c = TCanvas('cL', '', 1280, 720)
    l = TLegend(0.65, 0.3, 0.85, 0.85)
    l.AddEntry(0, 'Distanzen x / mm', '')
    first = True
    for i, g in enumerate(graphs):
        g.SetMarkerStyle(1)
        g.SetMarkerColor(int(round(51 + (100. - 51) / 11 * i)))
        g.GetXaxis().SetRangeUser(1e-6, 26e-6)
        if first:
            g.Draw('APX')
            g.SetMaximum(50)
            g.SetMinimum(0)
            first = False
        else:
            g.Draw('PX')
        l.AddEntry(g, 'x = %.2f' % distances[i][0], 'p')
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
    g.Draw('AP')
    
    fit = Fitter('fitXc', 'pol1(0)')
    fit.setParam(0, 'x0', 1)
    fit.setParam(1, 'm', 0.5e-6)
    fit.fit(g, 1e-6, 23e-6)
    fit.saveData('../calc/part2/dist_fit_xc.txt')
    
    l = TLegend(0.15, 0.7, 0.4, 0.85)
    l.AddEntry('xc', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit y = x_{0}+m*t', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'x_{0} = %.3f #pm %.3f' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.AddEntry(0, 'm = %.3e #pm %.0e' % (fit.params[1]['value'], fit.params[1]['error']), '')
    l.Draw()

    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/dist_fitXc.pdf', 'pdf')
    
    # calculate mu
    m, sm = fit.params[1]['value'], fit.params[1]['error']
    U, sU = 48.8, 1
    l = 30
    mu = m * l / U / 100  # /100 -> from mm in cm
    smu = mu * np.sqrt((sm/m)**2 + (sU/U)**2)
    with TxtFile('../calc/part2/dist_mu.txt', 'w') as f:
        f.writeline('\t', str(mu), str(smu))


def fitA(amps, times):
    listx, listsx = zip(*times)
    listy, listsy = zip(*amps)
    data = DataErrors.fromLists(listx, listy, listsx, listsy)

    c = TCanvas('cA', '', 1280, 720)
    g = data.makeGraph('A', 'Zeit t / s', 'A / V')
    g.Draw('AP')
    
    fit = Fitter('A', '[0]*exp(-(x)/[1])')
    fit.setParam(0, 'C', 5e-8)
    fit.setParam(1, 't_n', 45e-6)
    fit.fit(g, 1e-6, 23e-6)
    fit.saveData('../calc/part2/dist_fit_A.txt')
    
    l = TLegend(0.65, 0.65, 0.85, 0.85)
    l.AddEntry('A', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit y = C*exp(-t/#tau_{n})', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'C = %.3e #pm %.0e' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.AddEntry(0, '#tau_{n} = %.3e #pm %.0e' % (fit.params[1]['value'], fit.params[1]['error']), '')
    l.Draw()
    
    if PRINTGRAPHS:
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
    
    fit = Fitter('fitS', 'sqrt(2*[0]*x)')
    fit.setParam(0, 'D_{n}', 5e-8)
    fit.fit(g, 1e-6, 23e-6)
    fit.saveData('../calc/part2/dist_fit_sigma.txt')
    
    l = TLegend(0.15, 0.7, 0.4, 0.85)
    l.AddEntry('Sigma', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit y = #sqrt{2*D_{n}*t}', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'D_{n} = %.3e #pm %.0e' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.Draw()
    
    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/dist_fitSigma.pdf', 'pdf')


def evalDistances():
    params = getDistanceParams()
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
        sigs.append((param[4]['value'], param[4]['error']))

        # for plotting all data in one graph
        data.filterX(xmin, xmax)
        data.subtractUnderground(param[0]['value'], param[1]['value'], param[0]['error'], param[1]['error'], corrMatrix[0][1])
        data.multiplyY(1000)  # V -> mV
        data.addPoint(-1e-6, 0, 0, 0)  # otherwise SetRangeUser() doesn't work
        data.addPoint(30e-6, 0, 0, 0)  # otherwise SetRangeUser() doesn't work
        graphs.append(data.makeGraph('g', 'Zeit t / #mu s', 'Spannung U / mV'))

    plotDistances(graphs, distances)

    # fit params of gauss
    fitXc(distances, times)
    fitA(amps, times)
    fitSigma(sigs, times)


def main():
    setupROOT()
    evalDistances()


if __name__ == "__main__":
    main()
