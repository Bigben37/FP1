#!/usr/bin/python2.7
from functions import setupROOT, avgerrors  # make sure to add ../lib to your project path or copy file from there
from ringlaser import X0Data
from ROOT import TCanvas, TLegend, TLine
from fitter import Fitter  # make sure to add ../lib to your project path or copy file from there
from txtfile import TxtFile  # make sure to add ../lib to your project path or copy file from there
import numpy as np


def fitX0(period):
    # get data and make graph
    data = X0Data.fromPath('../data/T_%dms.txt' % period)
    c = TCanvas('c_%d' % period, '', 1280, 720)
    g = data.makeGraph('g_%d' % period, 'Differenzenfrequenz #Delta#nu / kHz', 'Auftreffpunkt x_{0}\' / mm')
    g.Draw('AP')

    # axis cross
    vline = TLine(0, 33, 0, 60)
    vline.Draw()

    # fit
    fit = Fitter('fit_%d' % period, 'pol1(0)')
    fit.setParam(0, 'x_{m}', 47)
    fit.setParam(1, 'm')
    fit.fit(g, min(data.getX()) - 3, max(data.getX()) + 3)
    fit.saveData('../calc/fit_T_%dms.txt' % period, 'w')

    # legend
    l = TLegend(0.15, 0.65, 0.4, 0.85)
    l.SetTextSize(0.025)
    l.AddEntry(g, 'Messreihe bei T = %d ms' % period, 'p')
    l.AddEntry(fit.function, 'Fit mit x_{0}\'(#Delta#nu) = x_{m} + m * #Delta#nu', 'l')
    fit.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.4f', '%.4f')], chisquareformat='%.2f')
    l.Draw()

    # print
    c.Update()
    c.Print('../img/fit_T_%dms.pdf' % period, 'pdf')

    return [(fit.params[0]['value'], fit.params[0]['error']), (fit.params[1]['value'], fit.params[1]['error'])]


def calcAlpha(T, sT, m, sm):
    # constants, lengths in mm
    L = 2149
    la = 6.3282e-4
    n = 1.457
    d = 12.7

    w = 2 * np.pi / T
    sw = w * sT / T
    alpha = la * L / (2 * n * d * m * w)
    salpha = alpha * np.sqrt((sm / m) ** 2 + (sw / w) ** 2)
    return alpha, salpha


def main():
    periods = [30, 45, 60]
    fitresults = []
    for period in periods:
        fitresults.append(fitX0(period))

    # output xm
    with TxtFile('../calc/fixed_T_xm.txt', 'w') as f:
        for i, result in enumerate(fitresults):
            f.writeline('\t', str(periods[i]), *map(str, result[0]))
        f.writeline('\t', *map(str, avgerrors(*zip(*zip(*fitresults)[0]))))  # weighted average

    # calculate + output alphas
    alphas = []
    for i, result in enumerate(fitresults):
        alphas.append(calcAlpha(periods[i], X0Data.ST, *result[1]))
    with TxtFile('../calc/fixed_T_alpha.txt', 'w') as f:
        for i, alpha in enumerate(alphas):
            f.writeline('\t', str(periods[i]), *map(str, alpha))
        f.writeline('\t', *map(str, avgerrors(*zip(*alphas))))
        
    # make latex tables for fit results an alphas
    with TxtFile('../src/fit_x0.tex', 'w') as f:
        f.write2DArrayToLatexTable(zip(*([(periods)] + zip(*zip(*fitresults)[0]) + zip(*zip(*fitresults)[1]))),
                                   ['$T$ / ms', '$x_m$ / mm', '$s_{x_m}$ / mm', '$m$ / (mm / kHz)', '$s_m$ / (mm / kHz)'],
                                   ['%d', '%.3f', '%.3f', '%.4f', '%.4f'],
                                   'Fitergebnisse von $x_0\'(\Delta \\nu)$ bei festen Perioden $T$.', 'tab:fit:x0')
    
    with TxtFile('../src/fit_x0_alpha.tex', 'w') as f:
        f.write2DArrayToLatexTable(zip(*([(periods)] + zip(*alphas))), ['$T$ / ms', '$\\alpha$', '$s_{\\alpha}$'], 
                                   ['%d', '%.3f', '%.3f'], 'Mitf\\"uhrungskoeffizienten bei festen Perioden $T$. ', 
                                   'tab:x0:alpha')


if __name__ == '__main__':
    setupROOT()
    main()
