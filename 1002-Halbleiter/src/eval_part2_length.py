#!/usr/bin/python2.7
import numpy as np
from functions import setupROOT, loadCSVToList, avgerrors
from halbleiter import P2SemiCon
from ROOT import TCanvas, TLegend
from fitter import Fitter
from numpy import append

def getParams():
    params = []
    params.append([[0.00875, 0, 0.001, 25e-6, 2.5e-6], 15e-6, 35e-6])
    params.append([[0.00875, 0, 0.001, 20e-6, 2.5e-6], 15e-6, 30e-6])
    params.append([[0, 0, 0.0015, 17.5e-6, 2.5e-6], 13e-6, 22e-6])
    params.append([[0.0025, 0, 0.002, 16e-6, 2.5e-6], 12.5e-6, 20e-6])
    params.append([[-0.003, 0, 0.003, 14e-6, 2.5e-6], 10e-6, 20e-6])
    params.append([[0.003, 0, 0.004, 12.5e-6, 2.5e-6], 7.5e-6, 17.5e-6])
    params.append([[-0.0005, 0, 0.006, 10e-6, 2.5e-6], 5e-6, 15e-6])
    params.append([[-0.003, 0, 0.008, 7.5e-6, 2.5e-6], 3e-6, 12.5e-6])
    params.append([[-0.001, 0, 0.0012, 6e-6, 2e-6], 4e-6, 8e-6])
    params.append([[-0.005, 0, 0.002, 4e-6, 1.5e-6], 2e-6, 6e-6])
    params.append([[-0.0015, 0, 0.003, 2.5e-6, 1e-6], 1e-6, 3.5e-6])
    return params
    
def getLenghts():
    # load data
    f = lambda x: x[0]
    lengths = loadCSVToList('../data/part2/length/lengths.txt')
    lengths = map(f, lengths)
    offsets = loadCSVToList('../data/part2/length/length_offset.txt')
    offsets = map(f, offsets)
    sl = 0.005
    
    # calculate average offset:
    offset = avgerrors(offsets, [sl]*len(offsets))

    # add offset
    return map(lambda x: (x + offset[0], np.sqrt(sl**2 + offset[1]**2)), lengths)

def evalLength(n, params):
    data = P2SemiCon.fromPath('../data/part2/length/ALL%04.d/F%04dCH1.CSV' % (n, n))
    g = data.makeGraph()
    c = TCanvas('c%d' % n, '', 1280, 720)
    g.SetMarkerStyle(1)
    g.Draw('AP')
    
    fit = Fitter('f', 'pol1(0) + gaus(2)')
    paramname = ['a', 'b', 'A', 'xc', 's']
    for i, param in enumerate(params[0]):
        fit.setParam(i, paramname[i], param)
    fit.fit(g, params[1], params[2])
    
    c.Update()
    c.Print('../img/part2/length%02d.pdf' % n, 'pdf')
    
    return fit.params


def fitAmplitude(params):
    pass

def main():
    setupROOT()
    params = getParams()
    fitparams = []
    for i in range(0, 11):
        fitparams.append[evalLength(i, params[i])]
    lengths = getLenghts()
        
    

if __name__ == "__main__":
    main()