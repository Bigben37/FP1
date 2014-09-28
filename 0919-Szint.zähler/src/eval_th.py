#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData
from fitter import Fitter
from txtfile import TxtFile
import functions as funcs
import numpy as np


def getStartValues():
    """returns guessed start values for single peak fit"""
    peaks = []
    peaks.append([[(0, 'a0', 0.1), (1, 'b0', 0), (2, 'A0', 1), (3, 'c0', 225), (4, 's0', 20)], 180, 320])
    peaks.append([[(0, 'a1', 0.1), (1, 'b1', 0), (2, 'A1', 0.3), (3, 'c1', 410), (4, 's1', 20)], 350, 450])
    peaks.append([[(0, 'a2', 0.3), (1, 'b2', 0), (2, 'A2', 0.2), (3, 'c2', 625), (4, 's2', 30)], 575, 650])
    peaks.append([[(0, 'a3', 0.1), (1, 'b3', 0), (2, 'A3', 0.75), (3, 'c3', 700), (4, 's3', 20)], 650, 775])
    peaks.append([[(0, 'a4', 0.1), (1, 'b4', 0), (2, 'A4', 0.5), (3, 'c4', 900), (4, 's4', 20)], 800, 950])
    peaks.append([[(0, 'a5', 0.1), (1, 'b5', 0), (2, 'A5', 0.25), (3, 'c5', 1050), (4, 's5', 30)], 975, 1125])
    peaks.append([[(0, 'a6', 2.5e-2), (1, 'b6', 0), (2, 'A6', 1e-2), (3, 'c6', 1300), (4, 's6', 20)], 1250, 1375])
    peaks.append([[(0, 'a7', 2.5e-2), (1, 'b7', 0), (2, 'A7', 2e-2), (3, 'c7', 1475), (4, 's7', 20)], 1400, 1600])
    peaks.append([[(0, 'a8', 2e-2), (1, 'b8', 0), (2, 'A8', 3e-2), (3, 'c8', 2100), (4, 's8', 50)], 1975, 2225])
    peaks.append([[(0, 'a9', 2e-3), (1, 'b9', 0), (2, 'A9', 1e-2), (3, 'c9', 6400), (4, 's9', 75)], 6150, 6600])

    return peaks


def singlePeakFit(g, debug=False):
    """fits every peak individually

    Arguments:
    g     -- graph
    debut -- if true prints values of found peaks to console (default=False)
    """
    peaks = getStartValues()

    params = []
    for i, peak in enumerate(peaks):
        fit = Fitter('fit%d' % i, 'pol1(0) + gaus(2)')
        fit.function.SetLineColor(i % 8 + 2)
        for param in peak[0]:
            fit.setParam(*param)
        fit.fit(g, peak[1], peak[2], '+')
        params.append([fit.params[2]['value'], fit.params[3]['value'], fit.params[3]['error'], fit.params[4]['value']])
        if debug:
            for j, par in fit.params.iteritems():
                print(par['name'], par['value'], par['error'])
            print('')
    return params


def multiPeakFit(g, uf, up, ): # TODO TBI
    """fits all peaks with one function
    
    Arguments:
    g      -- graph
    uf     -- underground function
    up     -- start parameter for underground function
    count  -- number of peaks
    params -- params for peaks
    """
    return None


def channelToEnergy(c, sc, gauge):
    """convert channel to energy with calculated energy gauge

    Arguments:
    c     -- channel
    sc    -- error of channel
    gauge -- fit parameter of energy-channel fit
    """
    # set params and erros of E = a + b*c
    a, sa = gauge[0]
    b, sb = gauge[1]
    rho = gauge[2][0]
    # calculate energy and error
    E = a + b * c
    sE = np.sqrt(sa ** 2 + c * rho * sa * sb + (c * sb) ** 2 + (b * sc) ** 2)

    return E, sE


def makeLegend(): #TODO TBI
    pass


def printGraph(c, g, path, xstart, xend, ystart, yend, isLog=False):
    """prints graph with given parameters

    Arguments:
    c      -- canvas
    g      -- graph
    path   -- relative path were graph is saved
    xstart -- lowest value on x-axis
    xend   -- highest value on x-axis
    ystart -- lowest value on y-axis
    yend   -- highest value on y-axis
    isLog  -- if true sets y-axis to logarithmic (default=False)
    """
    c.SetLogy(isLog)
    g.GetXaxis().SetRangeUser(xstart, xend)
    g.SetMinimum(ystart)
    g.SetMaximum(yend)
    g.Draw('APX')  # X = no error bars

    c.Update()
    c.Print(path, 'pdf')


def evalTh():
    data = SzintData.fromPath('../data/th.TKA')
    data.prepare()
    c = TCanvas('c', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMarkerStyle(1)
    
    printGraph(c, g, '../img/th_energyspectrum.pdf', 0, 6711, 1e-4, 2, True)

    params = singlePeakFit(g)  # single peak fit

    # calculate energies for peaks
    gauge = funcs.loadCSVToList('../calc/energy_gauge_raw.txt')
    energies = []
    for param in params:
        energies.append(channelToEnergy(param[1], param[2], gauge))

    # save peak and energy data
    with TxtFile('../calc/th_peaks_single.txt', 'w') as f:
        for i, param in enumerate(params):
            f.writeline('\t', 'Peak% 2d' % (i + 1), str(param[1]), str(param[2]), str(energies[i][0]), str(energies[i][1]))

    # make graphs for single peaks
    printGraph(c, g, '../img/th_peaks_single_01-10.pdf', 0, 6711, 1e-4, 2, True)
    printGraph(c, g, '../img/th_peaks_single_01-06.pdf', 150, 1175, 0.05, 1.15)
    printGraph(c, g, '../img/th_peaks_single_07-09.pdf', 1200, 2250, 0, 0.075)
    printGraph(c, g, '../img/th_peaks_single_10.pdf', 6100, 6700, 0, 0.01)

    """
    # make multi-peak fit
    fit = Fitter('f', 'pol2(0) + gaus(3) + gaus(6) + gaus(9) + gaus(12) + gaus(15) + gaus(18)')
    fit.function.SetNpx(10000)
    fit.setParam(0, 'a', 0.1)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'c', 0)
    params = params[:6]
    for i, param in enumerate(params):
        fit.setParam(3 * (i + 1) + 0, 'A%d' % (i + 1), param[0])
        fit.setParam(3 * (i + 1) + 1, 'c%d' % (i + 1), param[1])
        fit.setParam(3 * (i + 1) + 2, 's%d' % (i + 1), param[3])
    fit.fit(g, 190, 1150)
    fit.saveData('../calc/th_peaks.txt', 'w')"""

    # c.Update()
    # c.Print('../img/th_peaks.pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalTh()

if __name__ == "__main__":
    main()
