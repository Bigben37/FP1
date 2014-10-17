#!/usr/bin/python2.7
from functions import setupROOT
from hanle import HanleData, prepareGraph
from ROOT import TCanvas, TLegend
import numpy as np
from fitter import Fitter


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

def fitBVoltage(bdata, name=''):
    c = TCanvas('fitBV_%s' % name, '', 1280, 720)
    g = bdata.makeGraph('gBV_%s' % name, 'Zeit t / s', 'Spannung U / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')
    
    xmin = 0
    xmax = bdata.getX()[-1]  # point with largest x-value
    mean = g.GetMean()
    print(xmin, xmax, mean)
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

def main():
    data = HanleData.fromPath('../data/messungen/00_p23.tab', 1)
    bdata = HanleData.fromPath('../data/messungen/00_p23.tab', 2)
    data.convertTimeToB(*fitBVoltage(bdata, '00_p23.tab'))

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Zeit t / s', 'Intensit#ddot{a}t I / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')
    
    # fit = Fitter('fit', fitFuncLorentz, (-0.1, 0.1), 6)
    
    c.Update()
    c.Print('../img/00_p23.pdf', 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()
