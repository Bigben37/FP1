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
    return A * tau * (1 + (2 * (a * (x - b) * tau) ** 2) - np.cos(2 * phi) +
                      2 * a * (x - b) * tau * np.sin(2 * phi)) / (2 * (1 + (2 * a * (x - b) * tau) ** 2)) + c


def theta(x):
    return 1 if x > 0 else 0


def fitFuncBVoltage(x, par):
    x = x[0]
    a = par[0]
    b = par[1]
    c1 = par[2]
    c2 = par[3]
    return c1 * theta(a - x) + ((c2 - c1) / (b - a) * (x - a) + c1) * theta(x - a) * theta(b - x) + c2 * theta(x - b)


def getXStart(bdata, steps, delta):
    for i in xrange(bdata.getLength() - steps):
        passed = False
        for j in xrange(1, steps):
            passed = passed or (bdata.points[i][1] - bdata.points[i + j][1] > delta)
        if passed:
            return bdata.points[i][0]


def getXEnd(bdata, steps, delta):
    for i in reversed(xrange(steps, bdata.getLength())):
        passed = False
        for j in xrange(1, steps):
            passed = passed or (bdata.points[i - j][1] - bdata.points[i][1] > delta)
        if passed:
            return bdata.points[i][0]


def fitBVoltage(bdata, name):
    c = TCanvas('fitBV_%s' % name, '', 1280, 720)
    g = bdata.makeGraph('gBV_%s' % name, 'Zeit t / s', 'Spannung U / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')

    xmin = getXStart(bdata, bdata.getLength() / 10, 0.25)
    xmax = getXEnd(bdata, bdata.getLength() / 10, 0.25)
    fit = Fitter('fitBV_%s' % name, 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', -2. / 3)
    fit.fit(g, xmin, xmax, 'M')
    fit.saveData('../calc/fitBV_%s.txt' % name, 'w')
    
    l = TLegend(0.55, 0.6, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Messdaten', 'p')
    l.AddEntry(fit.function, 'Fit mit U(t) = a + b*t', 'l')
    fit.addParamsToLegend(l, [('%.4f', '%.4f'), ('%.4f', '%.4f')], chisquareformat='%.2f', advancedchi=True, units=['U', 'U/s'])
    l.Draw()

    c.Update()
    c.Print('../img/fitBV_%s.pdf' % name, 'pdf')

    return fit.function


def fitLorentzPeak(name, phi, T):
    # read data
    data = HanleData.fromPath('../data/messungen/%s.tab' % name, 1)
    bdata = HanleData.fromPath('../data/messungen/%s.tab' % name, 2)
    # convert time to B-field and show only points with -0.2mT < x < 0.2mT
    data.convertTimeToB(fitBVoltage(bdata, name))
    data.filterX(-0.2, 0.2)

    # make canvas + graph
    canvas = TCanvas('c_%s' % name, '', 1280, 720)
    g = data.makeGraph('g_%s' % name, 'Magnetfeld B / T', 'Intensit#ddot{a}t I / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')  # redraw points without errors to set points in front of errors

    # get fit params
    gJ = 1.4838
    muB = 9.27400968e-24
    hbar = 1.05457126e-34
    a = gJ * muB / hbar / 1e12  # in 1/(mT*ns)
    if phi == 45:
        xmin, xmax = -0.05, 0.05
        A = 0.02
        c = -0.5
    else:
        xmin, xmax = -0.1, 0.1
        A = -0.02
        c = 1
    phipar = np.deg2rad(phi)
    # fit graph
    fit = Fitter('fit_%s' % name, fitFuncLorentz, (xmin, xmax, 6))
    fit.setParam(0, '#tau', 120)
    fit.setParam(1, '#phi', phipar)
    fit.setParam(2, 'A', A)
    fit.setParam(3, 'a', a, True)
    fit.setParam(4, 'b', 0)
    fit.setParam(5, 'c', c)
    fit.fit(g, xmin, xmax)
    fit.saveData('../calc/fit_%s.txt' % name, 'w')

    # add legend
    if phi == 90:
        l = TLegend(0.11, 0.15, 0.4, 0.55)
    else:
        l = TLegend(0.11, 0.45, 0.4, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Messdaten', 'p')
    l.AddEntry(fit.function, 'Fit mit Lorentzkurve', 'l')
    fit.addParamsToLegend(l, format=[('%.2f', '%.2f'), ('%.2e', '%.1e'), ('%.2e', '%.1e'), '%.2e', ('%.2e', '%.1e'), ('%.3f', '%.3f')], 
                          chisquareformat='%.0f', advancedchi=True, units=['ns', 'rad', 'V/ns', '1/(mT*ns)', 'T', 'V'])
    l.Draw()

    # print to file

    canvas.Update()
    canvas.Print('../img/fit_%s.pdf' % name, 'pdf')

    return fit.params[0]['value'], fit.params[0]['error']


def main():
    # init tau-lists
    taus = dict()
    taus[0] = dict()
    taus[45] = dict()
    taus[90] = dict()
    for file in os.listdir(os.path.join(os.getcwd(), '../data/messungen/')):
        if file.endswith('.tab'):
            name = file[:-4]
            phi = int(name[:2])
            if name.count('_') == 1:
                T = int(name[-2:])
            else:
                T = int(name[4:6])
            if name[-3] == 'm':
                T *= -1
            taus[phi][T] = fitLorentzPeak(name, phi, T)

    for phi, Ttaus in taus.iteritems():
        with TxtFile('../calc/taus_%02d.txt' % phi, 'w') as f:
            for T, tau in Ttaus.iteritems():
                f.writeline('\t', str(T).rjust(3, ' '), str(tau[0]), str(tau[1]))

if __name__ == '__main__':
    setupROOT()
    main()
