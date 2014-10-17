#!/usr/bin/python2.7
from functions import setupROOT
from hanle import HanleData, prepareGraph
from ROOT import TCanvas, TLegend
import numpy as np
from fitter import Fitter
from txtfile import TxtFile
import os


def fitFuncLorentz(x, par):
    """Lorentz-Function for fit f(x; tau, phi, A, a, b, c)"""
    x = x[0]
    tau = par[0] 
    phi = par[1]
    A = par[2]  # amplitude
    a = par[3]  # g_J * mu_B / hbar
    b = par[4]  # offset B
    c = par[5]  # y-offset
    return A * tau *  (1 + (2 * (a * (x - b) * tau) ** 2) - np.cos(2*phi) + 
                       2 * a * (x -b) * tau * np.sin(2 * phi)) / (2 * (1 + (2 * a * (x -b) * tau) ** 2)) + c

def theta(x):
    return 1 if x > 0 else 0

def fitFuncBVoltage(x, par):
    x = x[0]
    a = par[0]
    b = par[1]
    c1 = par[2]
    c2 = par[3]
    return c1 * theta(a - x) + ( (c2 - c1) / (b - a) * (x - a) + c1 ) * theta(x-a) *theta(b - x) + c2 * theta(x - b)

def fitBVoltage(bdata, name):
    c = TCanvas('fitBV_%s' % name, '', 1280, 720)
    g = bdata.makeGraph('gBV_%s' % name, 'Zeit t / s', 'Spannung U / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')
    
    xmin = 0
    xmax = bdata.getX()[-1]  # point with largest x-value
    mean = g.GetMean()
    fit = Fitter('fitBV_%s' % name, fitFuncBVoltage, (xmin, xmax, 4))
    fit.setParam(0, 'a', (mean + xmin) / 2)
    fit.setParam(1, 'b', (mean + xmax) / 2)
    fit.setParam(2, 'c_{1}', 1.1)
    fit.setParam(3, 'c_{2}', -0.5)
    fit.fit(g, xmin, xmax, 'M')
    fit.saveData('../calc/fitBV_%s.txt' % name, 'w')
    
    c.Update()
    c.Print('../img/fitBV_%s.pdf' % name, 'pdf')
    
    return fit.function

def fitLorentzPeak(name):
    # read data
    data = HanleData.fromPath('../data/messungen/%s.tab' % name, 1)
    bdata = HanleData.fromPath('../data/messungen/%s.tab' % name, 2)
    # convert time to B-field and show only points with -0.2mT < x < 0.2mT
    data.convertTimeToB(fitBVoltage(bdata, name))
    data.filterX(-0.2, 0.2)

    # make canvas + graph
    c = TCanvas('c_%s' % name, '', 1280, 720)
    g = data.makeGraph('g_%s' % name, 'Magnetfeld B / T', 'Intensit#ddot{a}t I / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')  # redraw points without errors to set points in front of errors
    
    # get fit params
    gJ = 1.4838
    muB = 9.27400968e-24
    hbar = 1.05457126e-34
    a = gJ * muB / hbar / 1e12  # in 1/(mT*ns)
    phi = np.deg2rad(float(name[:2]))
    xmin, xmax = -0.1, 0.1
    # fit graph
    fit = Fitter('fit_%s' % name, fitFuncLorentz, (xmin, xmax, 6))
    fit.setParam(0, '#tau', 120)
    fit.setParam(1, '#phi', phi)
    fit.setParam(2, 'A', -0.02)
    fit.setParam(3, 'a', a, True)
    fit.setParam(4, 'b', 0)
    fit.setParam(5, 'c', 1)
    fit.fit(g, xmin, xmax, 'M')
    fit.saveData('../calc/fit_%s.txt' % name, 'w')  # TODO Fitter check covmatrix, fixed parameter
    
    c.Update()
    c.Print('../img/fit_%s.pdf' % name, 'pdf')
    
    return fit.params[0]['value'], fit.params[0]['error']

def main():
    #init tau-lists
    taus = dict()
    taus[0] = dict()
    taus[45] = dict()
    taus[90] = dict()
    print(taus)
    for file in os.listdir(os.path.join(os.getcwd(), '../data/messungen/')):
        if file.endswith('.tab'):
            name = file[:-4]
            phi = int(name[:2])
            T = int(name[-2:])
            if name[-3] == 'm':
                T *= -1
            taus[phi][T] = fitLorentzPeak(name)
            
    for phi, Ttaus in taus.iteritems():
        with TxtFile('../calc/taus_%02d.txt' % phi, 'w') as f:
            for T, tau in Ttaus.iteritems():
                f.writeline('\t', str(T).rjust(3, '+'), str(tau[0]), str(tau[1]))
                
if __name__ == '__main__':
    setupROOT()
    main()
