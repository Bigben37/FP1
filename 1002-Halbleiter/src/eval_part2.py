#!/usr/bin/python2.7
import numpy as np
from functions import setupROOT, loadCSVToList, avgerrors
from halbleiter import P2SemiCon
from ROOT import TCanvas, TLegend
from fitter import Fitter
from numpy import append
from data import DataErrors


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
    offsets = loadCSVToList('../data/part2/length/length_offset.txt')
    offsets = map(f, offsets)
    sd = 0.005

    # calculate average offset:
    offset = avgerrors(offsets, [sd] * len(offsets))

    # add offset
    return map(lambda x: (x + offset[0], np.sqrt(sd ** 2 + offset[1] ** 2)), distances)


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

    c.Update()
    c.Print('../img/part2/dist%02d.pdf' % n, 'pdf')

    return data, fit.params, fit.getCorrMatrix(), params[1], params[2]


def evalDistances():
    params = getDistanceParams()
    lengths = getDistances()
    fittedData = []   
    for i, param in enumerate(params):
        fittedData.append(evalDistance(i, param))
    
    graphs = []
    for data, param, corrMatrix, xmin, xmax in fittedData:
        data.filterX(xmin, xmax)
        data.subtractUnderground(param[0]['value'], param[1]['value'], param[0]['error'], param[1]['error'], corrMatrix[0][1])
        data.addPoint(0, 0, 0, 0)
        data.addPoint(30e-6, 0, 0, 0)
        graphs.append(data.makeGraph('g', 'Zeit t / #mu s', 'Spannung U / V'))
    
    c = TCanvas('cL', '', 1280, 720)
    l = TLegend(0.65, 0.3, 0.85, 0.85)
    l.AddEntry(0, 'Distanzen x / mm', '')
    first = True
    for i, g in enumerate(graphs):
        g.SetMarkerStyle(1)
        g.SetMarkerColor(int(round(51 + (100.-51) / 11 * i)))
        g.GetXaxis().SetRangeUser(1e-6, 27e-6)
        if first:
            g.Draw('APX')
            g.SetMaximum(0.05)
            g.SetMinimum(0)
            first = False
        else:
            g.Draw('PX')
        l.AddEntry(g, 'x = %.2f' % lengths[i][0], 'p')
    l.Draw()
    c.Update()
    c.Print('../img/part2/distances.pdf', 'pdf')

def main():
    setupROOT()
    evalDistances()


if __name__ == "__main__":
    main()
