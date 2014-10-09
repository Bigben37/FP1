#!/usr/bin/python2.7
from functions import setupROOT
from ROOT import TCanvas, TLegend, TF1
from halbleiter import P1SemiCon
from fitter import Fitter
import numpy as np


def evalErrors(elem):
    errorTransPyro = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxTrans.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CPYRO)).getY())
    errorTransSample = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxTrans.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)).getY())
    errorAbsPyro = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxAbs.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CPYRO)).getY())
    errorAbsSample = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxAbs.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)).getY())
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
    return data


def theta(x):
    if x > 0:
        return x
    return 0  # else


def absorpcoeff(E, Eg, T, AC, Ep):
    k = 0.000086  # in eV/K
    return AC * (theta(E - Eg + Ep) ** 2 / (np.exp(Ep / (k * T) - 1) + theta(E - Eg - Ep) ** 2 / (1 - np.exp(- Ep / (k * T)))))


def getAbsFunction(E, A0, l, Eg, T, AC, Ep):
    return A0 * np.exp(-absorpcoeff(E, Eg, T, AC, Ep) * l) * (1 - np.exp(-absorpcoeff(E, Eg, T, AC, Ep) * l))
    
def getTransFunction(E, T0, l, Eg, T, AC, Ep):
    return T0 * np.exp(- absorpcoeff(E, Eg, T, AC, Ep) * l)

def getAbsTransFitFunction(elem):
    consts = {'Si': [0.06, 0.061, 6199], 'Ge': [0.05, 0.036, 8823]}
    l, Ep, AC = consts[elem]
    fabs = lambda x, par: getAbsFunction(x[0], par[0], l, par[1], par[2], AC, Ep)
    ftrans = lambda x, par: getTransFunction(x[0], par[0], l, par[1], par[2], AC, Ep)
    return fabs, ftrans


def getFitParams(elem):
    params = []
    if elem == 'Si':
        params = [(0.8, 1.12, 180, 1, 1.3), (0.2, 1.12, 180, 1.075, 1.2)]
    return params

def fitAbsTrans(elem, filterx, ymax):
    # get errors
    errors = evalErrors(elem)
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
        g = data.makeGraph('g_%s_abstrans_%d' % (elem, i), P1SemiCon.LABELS[P1SemiCon.CENERGY], 'Intensit#ddot{a}t / b.E.')
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
    
    fitterabs = Fitter('fit_abs_%s' % elem, fabs, (filterx[0], filterx[1], 3))
    fitterabs.function.SetLineColor(colors[0][2])
    fitterabs.setParam(0, 'A_{0}', paramsabs[0])
    fitterabs.setParam(1, 'E_{g}', paramsabs[1])
    fitterabs.setParam(2, 'T', paramsabs[2])
    fitterabs.fit(graphs[0], paramsabs[3], paramsabs[4])
    fitterabs.saveData('../calc/part1/%s_fit_Abs.txt' % elem, 'w')
    
    fittertrans = Fitter('fit_trans_%s' % elem, ftrans, (filterx[0], filterx[1], 3))
    fittertrans.function.SetLineColor(colors[1][2])
    fittertrans.setParam(0, 'T_{0}', paramstrans[0])
    fittertrans.setParam(1, 'E_{g}', paramstrans[1])
    fittertrans.setParam(2, 'T', paramstrans[2])
    fittertrans.fit(graphs[1], paramstrans[3], paramstrans[4], '+')
    fittertrans.saveData('../calc/part1/%s_fit_Trans.txt' % elem, 'w')
    """
    f = TF1('fit_trans_%s' % elem, ftrans, filterx[0], filterx[1], 3)
    f.SetParameter(0, 0.185)
    f.SetParameter(1, 1.15)
    f.SetParameter(2, 300)
    f.Draw('SAME')
    """
    
    l = TLegend(0.7, 0.4, 0.99, 0.85)
    l.SetTextSize(0.02)
    l.AddEntry(graphs[0], 'Absorption Abs(E)', 'p')
    l.AddEntry(fitterabs.function, 'Fit mit Abs(E) = A_{0}*e^{-#alpha(E, E_{g}, T)*l} (1 - e^{-#alpha(E, E_{g}, T)*l})', 'l')
    fitterabs.addParamsToLegend(l, [('%.4f', '%.4f'), ('%.4f', '%.4f'), ('%.1f', '%.1f')], chisquareformat='%.2f')
    l.AddEntry(0, '', '')
    l.AddEntry(graphs[1], 'Transmission T(E)', 'p')
    l.AddEntry(fittertrans.function, 'Fit mit Trans(E) = T_{0}*e^{-#alpha(E, E_{g}, T)*l}', 'l')
    fittertrans.addParamsToLegend(l, [('%.4f', '%.4f'), ('%.4f', '%.4f'), ('%.1f', '%.1f')], chisquareformat='%.2f')
    l.Draw()
    
    c.Update()
    c.Print('../img/part1/%s_fit_AbsTrans.pdf' % elem, 'pdf')


def plotMultiChannelSpectrum(elem, mode, multichannels, rangeX, rangeY=(0, 5)):
    label = '%s_%s' % (elem, mode)

    c = TCanvas('c_spectrum_%s' % label, '', 1280, 720)
    graphs = []
    for channels in multichannels:
        data = P1SemiCon.fromPath('../data/part1/%s.txt' % label, channels)
        g = data.makeGraph('g_spectrum_%s' % label, P1SemiCon.LABELS[channels[0]], P1SemiCon.LABELS[channels[1]])
        g.SetMarkerStyle(1)
        g.SetMinimum(rangeY[0])
        g.SetMaximum(rangeY[1])
        g.GetXaxis().SetRangeUser(rangeX[0], rangeX[1])
        graphs.append(g)

    first = True
    for i, g in enumerate(graphs):
        if first:
            g.Draw('AP')
            first = False
        else:
            g.SetMarkerColor(1 + i)
            g.Draw('P')
    c.Update()
    c.Print('../img/part1/%s_spectrum.pdf' % label, 'pdf')


def evalPart1():
    elems = ['Si']#, 'Ge']
    filterxs = [(0, 1.8), (0, 0.85)]
    ymaxs = [0.25, 0.25]
    for elem, filterx, ymax in zip(elems, filterxs, ymaxs):
        fitAbsTrans(elem, filterx, ymax)
        plotMultiChannelSpectrum('Si', 'Messung', [(P1SemiCon.CANGLE, P1SemiCon.CPYRO), (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)], (-5, 80))
        plotMultiChannelSpectrum(elem, 'Lampe', [(P1SemiCon.CANGLE, P1SemiCon.CPYRO), (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)], (-5, 80))


def main():
    setupROOT()
    # TODO get errors
    evalPart1()


if __name__ == "__main__":
    main()
