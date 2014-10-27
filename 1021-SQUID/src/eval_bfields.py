#!/usr/bin/python2.7
from ROOT import TCanvas, TLegend, TLine, gPad

from data import Data
from fitter import Fitter
from functions import setupROOT, avgerrors
from txtfile import TxtFile

import numpy as np
from squid import SquidData, prepareGraph


fitparams = {'Spule_R1': (8, 50), 'Spule_R2': (0, 50), 'Spule_R3': (12, 40), 'Spule_R4': (10, 35), 'Spule_R5_1': (10, 30)}
RFBs = {1: 21e-3, 3: 60e-3, 6: 120e-3, 10: 195e-3, 15: 290e-3, 20: 380e-3, 50: 950e-3, 100: 1900e-3}


def ampToB(rfb, A, sA):
    """returns B-field in T"""
    B = 9.3e-9 * A / RFBs[rfb]
    sB = 9.3e-9 * sA / RFBs[rfb]
    return B, sB


def evalGraph(dir, name, rfb, mode='', omega=0):
    """create graph with optional fit

    Arguments:
    dir  -- directory
    name -- name of file with data (without extension)
    mode -- display mode. None (''), both signals ('both') and fitting ('fit')
    """
    even = SquidData.fromPath('../data/%s/%s_HM1508-2.csv' % (dir, name), True)
    if name == 'Magnetspan_0grad':
        even.setYErrorAbs(even.points[0][3] * 2)
    ymin = min(even.getY())
    ymax = max(even.getY())

    phi = 0

    c = TCanvas('c_%s' % name, '', 1280, 720)
    g = even.makeGraph('g_%s' % name, 'Zeit t / s', 'Spannung U / V')
    offset = g.GetMean(2)
    g.GetXaxis().SetLimits(0, 50)
    prepareGraph(g)
    g.Draw('AP')
    g.Draw('PX')
    if mode == 'both':  # print 2nd graph
        odd = SquidData.fromPath('../data/%s/%s_HM1508-2.csv' % (dir, name), False)
        godd = odd.makeGraph('godd_%s' % name, 'Zeit t / s', 'Spannung U / V')
        prepareGraph(godd)
        godd.SetMarkerColor(2)
        godd.SetLineColor(50)
        godd.Draw('P')
        godd.Draw('PX')

    xmin, xmax = 0, 50
    if mode == 'fit':
        # fit params
        if name in fitparams:
            xmin, xmax = fitparams[name]
        # fit
        fit = Fitter('fit_%s' % name, '[0]*sin([1]*x+[2]) + [3]')
        fit.function.SetNpx(1000)
        fit.setParam(0, 'A', (ymax - ymin) / 2)
        fit.setParam(1, '#omega', 2 * np.pi / 8)
        fit.setParam(2, '#phi', 0)
        fit.setParam(3, 'c', offset)
        fit.fit(g, xmin, xmax, 'M')
        fit.saveData('../calc/fit_%s.txt' % name)
        omega = fit.params[1]['value']
        phi = fit.params[2]['value']
        offset = fit.params[3]['value']

        # legend
        l = TLegend(0.675, 0.6, 0.995, 0.995)
        l.SetTextSize(0.03)
        l.AddEntry(g, 'Messung', 'p')
        l.AddEntry(fit.function, 'Fit mit U(t) A*sin(#omega*t+#phi) + c', 'l')
        fit.addParamsToLegend(l, [('%.5f', '%.5f'), ('%.2e', '%.1e'), ('%.3f', '%.3f'), ('%.2e', '%.1e'), ('%.2e', '%.1e')],
                              chisquareformat='%.2f', advancedchi=True,
                              units=['V', 'rad/s', 'rad', 'V', 'V/s'])
        l.Draw()

    c.Update()
    if mode:
        name2 = '_' + name
    else:
        name2 = name
    c.Print('../img/%s%s.pdf' % (mode, name2), 'pdf')

    even.filterX(xmin, xmax)
    makePolarPlot(even, name, omega, phi, rfb, offset)

    if mode == 'fit':
        return [(abs(fit.params[0]['value']), fit.params[0]['error']), (fit.params[1]['value'], fit.params[1]['error']),
                (fit.params[2]['value'], fit.params[2]['error'])]


def makePolarPlot(squiddata, name, omega, phi, si, offset):
    # generate polar data
    data = Data()
    for t, A, st, sA in squiddata.points:
        alpha = omega * t + phi
        B = abs(ampToB(si, A - offset, sA)[0])
        x = B * np.cos(alpha)
        y = B * np.sin(alpha)
        data.addPoint(x, y)
    # make canvas and graph
    c = TCanvas('c_polar_%s' % name, '', 1280, 1280)
    g = data.makeGraph('g_polar_%s' % name, 'B_{z} / T', 'B_{z} / T')
    g.SetMarkerStyle(1)
    g.Draw('AP')

    # set quatratic range
    gPad.Update()
    ymin = gPad.GetUymin()
    ymax = gPad.GetUymax()
    xmin = gPad.GetUxmin()
    xmax = gPad.GetUxmax()
    posdim = max(xmax, ymax)
    negdim = min(xmin, ymin)
    g.SetMinimum(negdim)
    g.SetMaximum(posdim)
    g.GetXaxis().SetLimits(negdim, posdim)
    if name == 'Spule_R5_1':
        gPad.SetLeftMargin(0.15)
        gPad.SetBottomMargin(0.15)
        g.GetYaxis().SetTitleOffset(1.5)
        g.GetXaxis().SetNdivisions(8 + 5 * 100)

    # draw axis cross
    vline = TLine(0, negdim, 0, posdim)
    vline.Draw()
    hline = TLine(negdim, 0, posdim, 0)
    hline.Draw()

    # print canvas
    c.Update()
    c.Print('../img/polar_%s.pdf' % name, 'pdf')


def main():
    evalGraph('141022', 'Spule_R1', 1, 'both')
    # make fits
    fitfiles = [('141022', 'Spule_R1', 100), ('141022', 'Spule_R2', 100), ('141022', 'Spule_R3', 100),
                ('141022', 'Spule_R4', 100), ('141022', 'Spule_R5_1', 100), ('141021', 'Magnet', 1),
                ('141022', 'Magnetspan_0grad', 100), ('141022', 'Magnetspan_45grad', 20),
                ('141022', 'Magnetspan_90grad', 50)]
    results = dict()
    rfbs = dict()
    for dir, file, rfb in fitfiles:
        results[file] = evalGraph(dir, file, rfb, 'fit')
        rfbs[file] = rfb

    # print fit results to file
    reslabels = {0: 'Amplitude', 1: 'omega', 2: 'phi'}
    for i, label in reslabels.iteritems():
        with TxtFile('../calc/%s.txt' % label, 'w') as f:
            for key in results:
                f.writeline('\t', key, *map(str, results[key][i]))

    # calculate b-field from fitted amplitudes
    bfields = [(key, results[key][0], ampToB(rfbs[key], *results[key][0])) for key in results]
    bfields.sort(key=lambda x: x[0])
    with TxtFile('../calc/bfields_fit.txt', 'w') as f:
        for key, res, bfield in bfields:
            f.writeline('\t', key, *map(str, res + bfield))
    with TxtFile('../calc/bfields_leiterschleife_fit.txt', 'w') as f:
        for key, res, bfield in bfields[-5:]:
            f.writeline('\t', *map(str, bfield))

    # calculate average omega
    omegas = [results[key][1] for key in results]
    avgomega = avgerrors(*zip(*omegas))
    with TxtFile('../calc/omega_avg.txt', 'w') as f:
        f.writeline('\t', *map(str, avgomega))

    # print graphs without fitting, averaged omega from fits is used for polar plot
    drawfiles = [('141022', 'Au-Plaettchen', 100), ('141022', 'emptyHolder', 100), ('141022', 'emptyHolder_afterShaking', 100),
                 ('141022', 'emptyHolder_perpendicular', 100), ('141022', 'Fe-Span', 100), ('141022', 'Stabmagnet_parallel', 1),
                 ('141022', 'Untergrund', 100)]
    for dir, file, rfb in drawfiles:
        evalGraph(dir, file, rfb, omega=avgomega[0])

if __name__ == '__main__':
    setupROOT()
    main()
