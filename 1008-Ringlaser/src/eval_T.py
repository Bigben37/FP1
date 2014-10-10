#!/usr/bin/python2.7
from functions import setupROOT, avgerrors, loadCSVToList  # make sure to add ../lib to your project path or copy file from there
from ringlaser import TData
from ROOT import TCanvas, TLegend, TLine
from fitter import Fitter  # make sure to add ../lib to your project path or copy file from there
from txtfile import TxtFile  # make sure to add ../lib to your project path or copy file from there
import numpy as np


def fitT(x0):
    # get data and make graph
    data = TData.fromPath('../data/x0_%dmm.txt' % x0)
    c = TCanvas('c_%d' % x0, ', 1280, 720')
    g = data.makeGraph('g_%d' % x0, 'Kreisfrequenz #omega / (1/ms)', 'Differenzenfrequenz #Delta #nu / kHz')
    g.Draw('AP')

    # fit
    fit = Fitter('fit_%d' % x0, 'pol1(0)')
    fit.setParam(0, 'a')
    fit.setParam(1, 'b')
    fit.fit(g, min(data.getX()) - 3, max(data.getX()) + 3)
    fit.saveData('../calc/fit_x0_%dmm.txt' % x0, 'w')

    # legend
    l = TLegend(0.15, 0.65, 0.46, 0.85)
    l.SetTextSize(0.025)
    l.AddEntry(g, 'Messreihe bei x_{0}\' = %d mm' % x0, 'p')
    l.AddEntry(fit.function, 'Fit mit #Delta#nu (#omega) = a + b*#omega', 'l')
    fit.addParamsToLegend(l, [('%.1f', '%.1f'), ('%.0f', '%.0f')], chisquareformat='%.2f')
    l.Draw()

    # print
    c.Update()
    c.Print('../img/fit_x0_%dmm.pdf' % x0, 'pdf')

    return [(fit.params[0]['value'], fit.params[0]['error']), (fit.params[1]['value'], fit.params[1]['error'])]


def getXm(path):
    data = loadCSVToList(path)
    return data[-1]


def calcAlpha(x, sx, xm, sxm, m, sm):
    # constants, lengths in mm
    L = 2149
    la = 6.3282e-4
    n = 1.457
    d = 12.7

    x0 = abs(x - xm)
    sx0 = np.sqrt(sx ** 2 + sxm ** 2)
    alpha = m * la * L / (2 * n * d * x0)
    salpha = alpha * np.sqrt((sm / m) ** 2 + (sx0 / x0) ** 2)
    return alpha, salpha


def main():
    x0s = [36, 40, 53, 57]
    fitresults = []
    for x0 in x0s:
        fitresults.append(fitT(x0))

    xm, sxm = getXm('../calc/fixed_T_xm.txt')
    alphas = []
    for i, result in enumerate(fitresults):
        alphas.append(calcAlpha(x0s[i], TData.SX, xm, sxm, *result[1]))
    with TxtFile('../calc/fixed_x0_alpha.txt', 'w') as f:
        for i, alpha in enumerate(alphas):
            f.writeline('\t', str(x0s[i]), *map(str, alpha))
        f.writeline('\t', *map(str, avgerrors(*zip(*alphas))))
    
    # make latex tables for fit results an alphas
    with TxtFile('../src/fit_T.tex', 'w') as f:
        f.write2DArrayToLatexTable(zip(*([(x0s)] + zip(*zip(*fitresults)[0]) + zip(*zip(*fitresults)[1]))),
                                   ['$x_0\'$ / mm', '$a$ / kHz', '$s_{a}$ / kHz', '$b$ / (kHz $\cdot$ ms)', '$s_b$ / (kHz $\cdot$ ms)'],
                                   ['%d', '%.1f', '%.1f', '%.0f', '%.0f'],
                                   'Fitergebnisse von $\Delta \\nu(\\omega)$ bei festen Auftrittpunkten $x_0\'$.', 'tab:fit:T')

    with TxtFile('../src/fit_T_alpha.tex', 'w') as f:
        f.write2DArrayToLatexTable(zip(*([(x0s)] + zip(*alphas))), ['$x_0\'$ / mm', '$\\alpha$', '$s_{\\alpha}$'], 
                                   ['%d', '%.3f', '%.3f'], 'Mitf\\"uhrungskoeffizienten bei festen Auftreffpunkten $x_0\'$. ', 
                                   'tab:T:alpha')


if __name__ == '__main__':
    setupROOT()
    main()
