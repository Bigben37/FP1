#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData, channelToEnergy, prepareGraph
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
        params.append([fit.params[2]['value'], fit.params[3]['value'], fit.params[3]['error'], fit.params[4]['value'], fit.function])
        if debug:
            for j, par in fit.params.iteritems():
                print(par['name'], par['value'], par['error'])
            print('')
    return params


def multiPeakFit(g, ufunc, uparams, params, xstart, xend):  # TODO TBI
    """fits all peaks with one function

    Arguments:
    g      -- graph
    ufunc     -- underground function
    uparams     -- start parameter for underground function
    params -- params for peaks
    xstart -- start x value
    xend   -- end x value
    """
    # build fit function
    fitfunc = ufunc
    pstart = len(uparams)
    for i in xrange(len(params)):
        fitfunc += ' + gaus(%d)' % (pstart + 3 * i)
    # create fitter, change npx to high value
    fit = Fitter('f', fitfunc)
    fit.function.SetNpx(10000)
    # set underground params
    for i, param in enumerate(uparams):
        fit.setParam(i, chr(97 + i), param)  # params of underground are enumerated with a, b, c, ...
    # set peak params
    for i, param in enumerate(params):
        fit.setParam(3 * i + pstart + 0, 'A%d' % (i + 1), param[0])
        fit.setParam(3 * i + pstart + 1, 'c%d' % (i + 1), param[1])
        fit.setParam(3 * i + pstart + 2, 's%d' % (i + 1), param[3])
    # fit
    fit.fit(g, xstart, xend)
    return fit


def makeLegend(xmin, ymin, xmax, ymax, peaks):  # TODO TBI
    l = TLegend(xmin, ymin, xmax, ymax)
    l.AddEntry('g', 'Messwerte', 'p')
    for peak in peaks:
        l.AddEntry(peak[0], peak[1], 'l')
    return l


def printGraph(c, g, path, xstart, xend, ystart, yend, options='P', isLog=False):
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
    g.Draw(options)  # X = no error bars

    c.Update()
    c.Print(path, 'pdf')


def evalTh():
    # load data
    data = SzintData.fromPath('../data/th.TKA')
    data.prepare()
    gauge = funcs.loadCSVToList('../calc/energy_gauge_raw.txt')

    # prepare canvas and graph
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    prepareGraph(g)

    printGraph(c, g, '../img/th_energyspectrum.pdf', 0, 6711, 1e-4, 2, 'APX', True)

    params = singlePeakFit(g)  # single peak fit

    # calculate energies for single peaks
    energies = []
    for param in params:
        energies.append(channelToEnergy(param[1], param[2], gauge))

    # save peak and energy data from single peaks
    with TxtFile('../calc/th_peaks_single.txt', 'w') as f:
        for i, param in enumerate(params):
            f.writeline('\t', 'Peak% 2d' % (i + 1), str(param[1]), str(param[2]), str(energies[i][0]), str(energies[i][1]))


    # make graphs for single peaks
    peaklegend = zip(zip(*params)[4], map(lambda i: "Peak % 2d" % i, xrange(1, 11)))
    printGraph(c, g, '../img/th_peaks_single_01-10.pdf', 0, 6711, 1e-4, 2, isLog=True)
    
    l = makeLegend(0.6, 0.6, 0.85, 0.85, peaklegend[:6])
    l.Draw()
    printGraph(c, g, '../img/th_peaks_single_01-06.pdf', 150, 1175, 0.05, 1.15)
    
    l = makeLegend(0.15, 0.6, 0.3, 0.85, peaklegend[6:9])
    l.Draw()
    printGraph(c, g, '../img/th_peaks_single_07-09.pdf', 1200, 2250, 0, 0.075)
    
    l = makeLegend(0.7, 0.7, 0.85, 0.85, peaklegend[9:10])
    l.Draw()
    printGraph(c, g, '../img/th_peaks_single_10.pdf', 6100, 6700, 0, 0.01)
    

    multichannels = []
    # make multi peak fit -- 1 to 6
    fit = multiPeakFit(g, 'pol2(0)', [0.1, 0, 0], params[:6], 190, 1150)
    fit.saveData('../calc/th_peaks_multi_01-06.txt', 'w')
    l = makeLegend(0.7, 0.7, 0.85, 0.85, [[fit.function, 'Peaks 1 bis 6']])
    l.Draw()
    printGraph(c, g, '../img/th_peaks_multi_01-06.pdf', 150, 1175, 0.05, 1.15)
    for i in xrange(4, 20, 3):
        multichannels.append([fit.params[i]['value'], fit.params[i]['error']])
    # make multi peak fit -- 7 to 8
    fit = multiPeakFit(g, 'pol2(0)', [0.02, 0, 0], params[6:8], 1250, 1650)
    fit.saveData('../calc/th_peaks_multi_07-08.txt', 'w')
    l = makeLegend(0.7, 0.7, 0.85, 0.85, [[fit.function, 'Peaks 7 und 8']])
    l.Draw()
    printGraph(c, g, '../img/th_peaks_multi_07-08.pdf', 1225, 1675, 0.01, 0.05)
    for i in xrange(4, 8, 3):
        multichannels.append([fit.params[i]['value'], fit.params[i]['error']])

    # calculate energies for multi peaks
    energies = []
    for channel in multichannels:
        energies.append(channelToEnergy(channel[0], channel[1], gauge))

    # save peak and energy data from multi peaks
    with TxtFile('../calc/th_peaks_multi.txt', 'w') as f:
        for i, channel in enumerate(multichannels):
            f.writeline('\t', 'Peak% 2d' % (i + 1), str(channel[0]), str(channel[1]), str(energies[i][0]), str(energies[i][1]))


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalTh()

if __name__ == "__main__":
    main()
