#!/usr/bin/python2.7
from functions import setupROOT, avgerrors
from ROOT import TCanvas, TLegend, TLine
from halbleiter import P1SemiCon
from fitter import Fitter
from txtfile import TxtFile
import numpy as np


def evalYErrors(elem):
    errorTransPyro = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxTrans.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CPYRO)).getY(), ddof=1)
    errorTransSample = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxTrans.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)).getY(), ddof=1)
    errorAbsPyro = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxAbs.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CPYRO)).getY(), ddof=1)
    errorAbsSample = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxAbs.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)).getY(), ddof=1)
    return max(errorAbsPyro, errorTransPyro), max(errorAbsSample, errorTransSample)


def calcRealIntensity(elem, channel, error):
    # get measurement, underground and spectrum of lamp
    data = P1SemiCon.fromPath('../data/part1/%s_Messung.txt' % elem, (P1SemiCon.CENERGY, channel))
    data.setYErrorAbs(error)
    underground = P1SemiCon.fromPath('../data/part1/%s_Untergrund.txt' % elem, (P1SemiCon.CENERGY, channel))
    data.setYErrorAbs(error)
    lamp = P1SemiCon.fromPath('../data/part1/%s_Lampe.txt' % elem, (P1SemiCon.CENERGY, P1SemiCon.CPYRO))
    lamp.setYErrorAbs(error)

    # calculate real itensity
    data.subtractUnderground(underground)
    data.normalize(lamp)
    data.setXErrorRel(0.01)
    return data


def theta(x):
    if x > 0:
        return x
    return 0  # else


def absorpcoeff(E, Eg, T, AC, Ep):
    k = 0.000086  # in eV/K
    return AC * (theta(E - Eg + Ep) ** 2 / (np.exp(Ep / (k * T) - 1) + theta(E - Eg - Ep) ** 2 / (1 - np.exp(- Ep / (k * T)))))


def getAbsFunction(E, A0, l, d, Eg, T, AC, Ep, y0):
    return A0 * np.exp(-absorpcoeff(E, Eg, T, AC, Ep) * d) * (1 - np.exp(-absorpcoeff(E, Eg, T, AC, Ep) * (l - d))) + y0


def getTransFunction(E, T0, l, Eg, T, AC, Ep):
    return T0 * np.exp(- absorpcoeff(E, Eg, T, AC, Ep) * l)


def getAbsTransFitFunction(elem):
    consts = {'Si': [0.06, 0.061, 6199], 'Ge': [0.05, 0.036, 8823]}
    l, Ep, AC = consts[elem]
    T = 293.15
    fabs = lambda x, par: getAbsFunction(x[0], par[0], l, par[1], par[2], T, AC, Ep, par[3])
    ftrans = lambda x, par: getTransFunction(x[0], par[0], l, par[1], T, AC, Ep)
    return fabs, ftrans


def getFitParams(elem):
    params = []  # [(abs), (trans)] = [(A0, d, Eg, y0, xmin, xmax), (T0, Eg, xmin, xmax)]
    if elem == 'Si':
        params = [(0.2, 0.005, 1.12, 0, 1, 1.35), (0.2, 1.12, 1.075, 1.3)]
    elif elem == 'Ge':
        params = [(0.2, 0.005, 0.67, 0, 0.55, 0.8), (0.2, 0.67, 0.65, 0.8)]
    return params


def fitAbsTrans(elem, filterx, ymax):
    # get errors
    errors = evalYErrors(elem)
    with TxtFile('../calc/part1/%s_yerrors.txt' % elem, 'w') as f:
        f.writeline('\t', *map(str, errors))

    # get absoprtion and transmission data
    abs = calcRealIntensity(elem, P1SemiCon.CSAMPLE, errors[1])
    abs.filterX(*filterx)
    trans = calcRealIntensity(elem, P1SemiCon.CPYRO, errors[0])
    trans.filterX(*filterx)
    datas = [abs, trans]

    # make Graphs
    c = TCanvas('c_%s' % elem, '', 1280, 720)
    graphs = []
    colors = [(1, 16, 2), (4, 36, 6)]
    for i, data in enumerate(datas):
        g = data.makeGraph('g_%s_abstrans_%d' % (elem, i), P1SemiCon.LABELS[P1SemiCon.CENERGY], 'Intensit#ddot{a}ten I_{Pyro}, I_{Probe}')
        g.SetMinimum(0)
        g.SetMaximum(ymax)
        g.SetMarkerStyle(8)
        g.SetMarkerSize(0.3)
        g.SetMarkerColor(colors[i][0])
        g.SetLineWidth(0)
        g.SetLineColor(colors[i][1])
        graphs.append(g)
    graphs[0].Draw('AP')
    graphs[1].Draw('P')

    # fit methods
    fabs, ftrans = getAbsTransFitFunction(elem)
    paramsabs, paramstrans = getFitParams(elem)

    fitterabs = Fitter('fit_abs_%s' % elem, fabs, (filterx[0], filterx[1], 4))
    fitterabs.function.SetLineColor(colors[0][2])
    fitterabs.setParam(0, 'A_{0}', paramsabs[0])
    fitterabs.setParam(1, 'd', paramsabs[1])
    fitterabs.setParam(2, 'E_{g}', paramsabs[2])
    fitterabs.setParam(3, 'y_{0}', paramsabs[3])
    fitterabs.fit(graphs[0], paramsabs[4], paramsabs[5])
    fitterabs.saveData('../calc/part1/%s_fit_Abs.txt' % elem, 'w')

    fittertrans = Fitter('fit_trans_%s' % elem, ftrans, (filterx[0], filterx[1], 2))
    fittertrans.function.SetLineColor(colors[1][2])
    fittertrans.setParam(0, 'T_{0}', paramstrans[0])
    fittertrans.setParam(1, 'E_{g}', paramstrans[1])
    fittertrans.fit(graphs[1], paramstrans[2], paramstrans[3], '+')
    fittertrans.saveData('../calc/part1/%s_fit_Trans.txt' % elem, 'w')

    l = TLegend(0.65, 0.4, 0.99, 0.85)
    l.SetTextSize(0.02)
    l.AddEntry(graphs[0], 'Absorption Abs(E)', 'p')
    l.AddEntry(fitterabs.function, 'Fit mit Abs(E) = A_{0}*e^{-#alpha(E, E_{g})*d} (1 - e^{-#alpha(E, E_{g})*(l-d)}) + y_{0}', 'l')
    fitterabs.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.4f', '%.4f'), ('%.4f', '%.4f'), ('%.5f', '%.5f')], chisquareformat='%.2f')
    l.AddEntry(0, '', '')
    l.AddEntry(graphs[1], 'Transmission Trans(E)', 'p')
    l.AddEntry(fittertrans.function, 'Fit mit Trans(E) = T_{0}*e^{-#alpha(E, E_{g})*l}', 'l')
    fittertrans.addParamsToLegend(l, [('%.4f', '%.4f'), ('%.3f', '%.3f')], chisquareformat='%.2f')
    l.Draw()

    c.Update()
    c.Print('../img/part1/%s_fit_AbsTrans.pdf' % elem, 'pdf')

    return (fitterabs.params[2]['value'], fitterabs.params[2]['error']), (fittertrans.params[1]['value'], fittertrans.params[1]['error'])


def calcWMinMax(phi):
    psi = np.radians(7.5)
    D = 2.5  # in cm
    L = 55  # in cm
    d = 2  # in cm
    wmin = psi + np.arcsin(np.sin(psi) - (D / 2 * np.cos(phi) + d / 2 * np.cos(psi)) / L)
    wmax = psi + np.arcsin(np.sin(psi) + (D / 2 * np.cos(phi) + d / 2 * np.cos(psi)) / L)
    return wmin, wmax


def calcsE(phi):
    print(np.rad2deg(phi))
    psi = np.radians(7.5)
    h = 4.136e-15  # in eV / s
    c = 2.999e8  # in m/s
    d = 0.02  # in m
    wmin, wmax = calcWMinMax(phi)
    #print(np.rad2deg(wmin), np.rad2deg(wmax))
    return 0.5 * (h * c / (2 * d * np.cos(psi) * np.sin(wmin / 2)) - h * c / (2 * d * np.cos(psi) * np.sin(wmax / 2)))

def convertEnergyToAngle(E, elem):
    h = 4.136e-15  # in eV / s
    c = 2.999e8  # in m/s
    psi = np.radians(7.5)
    if elem == 'Si':
        d = 1 / 1200e3
    elif elem == 'Ge':
        d = 1 / 600e3
    return np.arcsin( h * c / (2 * d * E * np.cos(psi)))


def plotMultiChannelSpectrum(elem, mode, multichannels, legendlabels, rangeX, rangeY=(0, 5.5), connect=False, addlabel=''):
    label = '%s_%s' % (elem, mode)
    drawoptions = 'L' if connect else ''

    c = TCanvas('c_spectrum_%s' % label, '', 1280, 720)
    graphs = []
    l = TLegend(0.6, 0.8 - len(multichannels) * 0.05, 0.85, 0.85)
    for i, channels in enumerate(multichannels):
        data = P1SemiCon.fromPath('../data/part1/%s.txt' % label, channels)
        g = data.makeGraph('g_spectrum_%s' % label, P1SemiCon.LABELS[channels[0]], P1SemiCon.LABELS[channels[1]])
        g.SetMarkerStyle(1)
        g.SetMinimum(rangeY[0])
        g.SetMaximum(rangeY[1])
        g.GetXaxis().SetRangeUser(rangeX[0], rangeX[1])
        g.SetLineWidth(0)
        g.SetMarkerStyle(8)
        g.SetMarkerSize(0.4)

        l.AddEntry(g, legendlabels[i], 'pl')

        graphs.append(g)

    first = True
    for i, g in enumerate(graphs):
        if first:
            g.SetMarkerColor(2)
            g.SetLineColor(2)
            g.Draw('AP' + drawoptions)
            first = False
        else:
            g.SetMarkerColor(3 + i)
            g.SetLineColor(3 + i)
            g.Draw('P' + drawoptions)
    l.Draw()

    vline = TLine(0, rangeY[0], 0, rangeY[1])
    vline.Draw()

    c.Update()
    c.Print('../img/part1/%s_spectrum%s.pdf' % (label, addlabel), 'pdf')


def main():
    setupROOT()
    elems = ['Si', 'Ge']
    filterxs = [(0, 1.8), (0, 1)]
    ymaxs = [0.25, 0.25]
    yundergrounds = [0.03, 0.1]
    energies = []
    for elem, filterx, ymax, yunderground in zip(elems, filterxs, ymaxs, yundergrounds):
        energies.append(fitAbsTrans(elem, filterx, ymax))
        plotMultiChannelSpectrum(elem, 'Messung',
                                 [(P1SemiCon.CANGLE, P1SemiCon.CPYRO), (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)],
                                 ['Signal des Pyrodetektors', 'Signal der Probe'], (-5, 80), connect=True)
        plotMultiChannelSpectrum(elem, 'Untergrund',
                                 [(P1SemiCon.CANGLE, P1SemiCon.CPYRO), (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)],
                                 ['Untergrund des Pyrodetektors', 'Untergrund der Probe'], (-5, 80), (0, yunderground))
        plotMultiChannelSpectrum(elem, 'Lampe', [(P1SemiCon.CANGLE, P1SemiCon.CPYRO)], ['Signal des Pyrodetektors'], (-5, 80), connect=True)
        plotMultiChannelSpectrum(elem, 'Messung',
                                 [(P1SemiCon.CANGLE, P1SemiCon.CENERGY)],
                                 ['Energie E(#alpha)'], (0, 80), connect=True, addlabel='_ea')

    for i, energie in enumerate(energies):
        with TxtFile('../calc/part1/%s_bandgap_avg.txt' % elems[i], 'w') as f:
            f.writeline('\t', *map(str, avgerrors(*zip(*energie))))
        with TxtFile('../calc/part1/%s_bandgap_syserror.txt' % elems[i], 'w') as f:
            for e, se in energie:
                sesys = calcsE(convertEnergyToAngle(e, elems[i]))
                f.writeline('\t', str(e), str(se), str(sesys), str(np.sqrt(se ** 2 + sesys ** 2)))
            


if __name__ == "__main__":
    main()
