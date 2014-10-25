#!/usr/bin/python2.7
"""Fit lorentz peaks"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"


from ROOT import TCanvas, TLegend
import os

# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from fitter import Fitter
from functions import setupROOT
from txtfile import TxtFile
# ========================================================================

from hanle import HanleData, prepareGraph
import numpy as np


def fitFuncLorentz(x, par):
    """Lorentz-Function for fit f(x; tau, phi, A, a, b, c)"""
    x = x[0]  # x
    tau = par[0]  # lifespan
    phi = par[1]  # angle
    A = par[2]  # amplitude
    a = par[3]  # g_J * mu_B / hbar
    b = par[4]  # offset B
    c = par[5]  # y-offset
    return A * tau * (1 + (2 * (a * (x - b) * tau) ** 2) - np.cos(2 * phi) +
                      2 * a * (x - b) * tau * np.sin(2 * phi)) / (2 * (1 + (2 * a * (x - b) * tau) ** 2)) + c


def getXStart(bdata, steps, delta):
    """Get start x-value of ramp

    Arguments:
    bdata -- U-t ramp
    steps -- x-interval
    delta -- y-interval
    """
    for i in xrange(bdata.getLength() - steps):
        passed = False
        for j in xrange(1, steps):
            passed = passed or (bdata.points[i][1] - bdata.points[i + j][1] > delta)
        if passed:
            return bdata.points[i][0]


def getXEnd(bdata, steps, delta):
    """Get end x-value of ramp

    Arguments:
    bdata -- U-t ramp
    steps -- x-interval
    delta -- y-interval
    """
    for i in reversed(xrange(steps, bdata.getLength())):  # go from highest to lowest x
        passed = False
        for j in xrange(1, steps):
            passed = passed or (bdata.points[i - j][1] - bdata.points[i][1] > delta)
        if passed:
            return bdata.points[i][0]


def fitBVoltage(bdata, name):
    """Fit ramp for b-field

    Arguments:
    bdata -- data
    name  -- filename
    """
    # make canvas and graphs
    c = TCanvas('fitBV_%s' % name, '', 1280, 720)
    g = bdata.makeGraph('gBV_%s' % name, 'Zeit t / s', 'Spannung U / V')
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')  # set points in foreground, errors in background

    # fit linear ramp, start and end value of x-axis (time) are obtained by getXStart and getXend
    xmin = getXStart(bdata, bdata.getLength() / 10, 0.25) + 0.1
    xmax = getXEnd(bdata, bdata.getLength() / 10, 0.25) - 0.1
    fit = Fitter('fitBV_%s' % name, 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', -2. / 3)
    fit.fit(g, xmin, xmax, 'M')
    fit.saveData('../calc/fitBV_%s.txt' % name, 'w')

    # draw legend
    l = TLegend(0.55, 0.6, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Messdaten', 'p')
    l.AddEntry(fit.function, 'Fit mit U(t) = a + b*t', 'l')
    fit.addParamsToLegend(l, [('%.4f', '%.4f'), ('%.4f', '%.4f')], chisquareformat='%.2f', advancedchi=True, units=['U', 'U/s'])
    l.Draw()

    # print canvas to file
    c.Update()
    c.Print('../img/fitBV_%s.pdf' % name, 'pdf')

    return fit.function


def normPhi(phi):
    """normalize angle to -180 deg < angle < 180 deg, in this case the angle is pi-periodic

    Arguments:
    phi -- angle
    """
    while phi < -np.pi:
        phi += np.pi
    while phi > np.pi:
        phi -= np.pi
    return phi


def fitLorentzPeak(name, phi, T):
    """fit lorentz peak

    Arguments:
    name -- filename
    phi  -- angle
    T    -- temperature
    """
    # read data
    data = HanleData.fromPath('../data/messungen/%s.tab' % name, 1)
    data.setYErrorFunc(lambda x: np.sqrt((0.01 * x) ** 2 + data.points[0][3] ** 2))  # bin error and relative error
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

    # get initial fit parameters
    gJ = 1.4838
    muB = 9.27400968e-24
    hbar = 1.05457126e-34
    a = gJ * muB / hbar / 1e12  # in 1/(mT*ns)
    b = 0
    if phi == 45:
        xmin, xmax = -0.05, 0.05
        A = 0.02
        c = -0.5
    else:
        xmin, xmax = -0.1, 0.1
        A = -0.02
        c = 1
    if T == -8 and phi == 0:  # special case, wont fit with 0.01
        xmin, xmax = -0.075, 0.075
    phipar = np.deg2rad(phi)
    # fit data
    fit = Fitter('fit_%s' % name, fitFuncLorentz, (xmin, xmax, 6))
    fit.setParam(0, '#tau', 120)
    fit.setParam(1, '#phi', phipar)
    fit.setParam(2, 'A', A)
    fit.setParam(3, 'a', a, True)
    fit.setParam(4, 'b', b)
    fit.setParam(5, 'c', c)
    fit.fit(g, xmin, xmax, 'M')
    fit.saveData('../calc/fit_%s.txt' % name, 'w')

    # add legend
    if phi == 90:
        l = TLegend(0.11, 0.15, 0.4, 0.55)
    else:
        l = TLegend(0.11, 0.45, 0.4, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Messdaten', 'p')
    l.AddEntry(fit.function, 'Fit mit Lorentzkurve', 'l')
    fit.addParamsToLegend(l,
                          format=[('%.2f', '%.2f'), ('%.2e', '%.1e'), ('%.2e', '%.1e'), '%.2e',
                                  ('%.2e', '%.1e'), ('%.3f', '%.3f')],
                          chisquareformat='%.2f', advancedchi=True, units=['ns', 'rad', 'V/ns', '1/(mT*ns)', 'T', 'V'])
    l.Draw()

    # print to file
    canvas.Update()
    canvas.Print('../img/fit_%s.pdf' % name, 'pdf')

    # return lifespan (tau) and angle (phi)
    return (fit.params[0]['value'], fit.params[0]['error']), (normPhi(fit.params[1]['value']), fit.params[1]['error'])


def main():
    # initialize data lists
    taus = {0: dict(), 45: dict(), 90: dict()}
    fitphis = {0: dict(), 45: dict(), 90: dict()}
    # initialize error lists
    errortaus = {0: [], 90: []}
    errorphis = {0: [], 90: []}
    errortemps = dict()
    # fit all data, all files with the pattern '../data/messungen/*.tab' will be detected and fitted
    for file in os.listdir(os.path.join(os.getcwd(), '../data/messungen/')):
        if file.endswith('.tab'):
            # parse file name to get temperature T and angle position phi
            name = file[:-4]
            phi = int(name[:2])
            if name.count('_') == 1:
                T = int(name[-2:])
            else:
                T = int(name[4:6])
            if name[-3] == 'm':
                T *= -1
            # get tau and phi of fit
            if name[-2] == '_':  # measurement with multiple data for same T and phi for errors
                tau, fitphi = fitLorentzPeak(name, phi, T)
                errortaus[phi].append(tau)
                errorphis[phi].append(fitphi)
                errortemps[phi] = T
            else:
                taus[phi][T], fitphis[phi][T] = fitLorentzPeak(name, phi, T)

    # get errors for 0 and 90 deg
    relTauErrors = dict()
    relPhiOffsetErrors = dict()
    # error for taus
    if errortaus[0] and errortaus[90]:
        for phi, taulist in errortaus.iteritems():  # for each angle
            # take average and standard deviation (with factor 1/(N-1))
            avg = np.average(zip(*taulist)[0])
            stdev = np.std(zip(*taulist)[0], ddof=1)
            # write single taus and avg+stdev
            with TxtFile('../calc/errortaus_%02d.txt' % phi, 'w') as f:
                for tau, error in taulist:
                    f.writeline('\t', str(tau), str(error))
                f.writeline('avg + stdev')
                f.writeline('\t', str(avg), str(stdev))
            # set average tau in tau list, error is stdev
            taus[phi][errortemps[phi]] = avg, stdev
            # calculate relative error
            relTauErrors[phi] = stdev / avg
        relTauErrors[45] = np.average(relTauErrors.values())  # average over 0 and 90 error
    # error for fit phis (is not used because not important for evaluation)
    if errorphis[0] and errorphis[90]:
        for phi, phioffsetlist in errorphis.iteritems():
            avg = np.average(zip(*phioffsetlist)[0])
            stdev = np.std(zip(*phioffsetlist)[0], ddof=1)
            with TxtFile('../calc/errorphioffsets_%02d.txt' % phi, 'w') as f:
                for offset, error in phioffsetlist:
                    f.writeline('\t', str(np.rad2deg(offset)), str(np.rad2deg(error)))
                f.writeline('avg + stdev')
                f.writeline('\t', str(np.rad2deg(avg)), str(np.rad2deg(stdev)))
            fitphis[phi][errortemps[phi]] = avg, stdev
            relPhiOffsetErrors[phi] = avg, stdev
        relPhiOffsetErrors[45] = np.average(relPhiOffsetErrors.values())  # average over 0 and 90 error

    # print fitted taus and phis with corrected error for taus but error from fit for phis
    for phi, Ttaus in taus.iteritems():
        with TxtFile('../calc/taus_%02d.txt' % phi, 'w') as f:
            for T, tau in Ttaus.iteritems():
                f.writeline('\t', str(T).rjust(3, ' '), str(tau[0]), str(tau[0] * relTauErrors[phi]),
                            str(np.rad2deg(fitphis[phi][T][0])), str(np.rad2deg(fitphis[phi][T][1])))

if __name__ == '__main__':
    setupROOT()
    main()
