#!/usr/bin/python2.7
from functions import setupROOT, loadCSVToList
from halbleiter import P3SemiCon, prepareGraph
from ROOT import TCanvas, TLegend
from fitter import Fitter
from data import DataErrors
from txtfile import TxtFile
import numpy as np


PRINTGRAPHS = True  # set false for faster debugging


def getParams(detector, element):
    params = []
    if detector == 'CdTe' and element == 'Am':
        params.append([(1e4, 285, 10), (272.5, 300), (200, 350), (0, 560)])
    elif detector == 'Si' and element == 'Am':
        params.append([(800, 300, 10), (270, 330), (250, 340), (0, 60)])
    elif detector == 'CdTe' and element == 'Co':
        params.append([(3750, 600, 10), (585, 610), (560, 630), (0, 280)])
        params.append([(600, 675, 20), (640, 700), (620, 720), (0, 30)])
    elif detector == 'Si' and element == 'Co':
        params.append([(250, 600, 20), (580, 650), (570, 660), (0, 22)])
        params.append([(), (670, 710), (650, 750), (0, 3)])
    return params


def printTotalSpectrum(data, element, detector, logy=True):
    c = TCanvas('total_%s-%s' % (element, detector), '', 1280, 720)
    c.SetLogy(logy)
    g = data.makeGraph('g%s-%s' % (element, detector), 'Kanal k', 'Counts N')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 2500)
    g.SetMinimum(0.9)
    g.Draw('APX')
    c.Update()
    if PRINTGRAPHS:
        c.Print('../img/part3/%s-%s_spectrum.pdf' % (element, detector), 'pdf')


def fitSpectrum(detector, element, params, logy=True):
    data = P3SemiCon.fromPath('../data/part3/%s-%s.mca' % (element, detector))
    printTotalSpectrum(data, element, detector, logy)

    fitresults = []
    for i, peak in enumerate(params):
        c = TCanvas('cpeakl_%s-%s_%d' % (element, detector, i), '', 1280, 720)
        g = data.makeGraph('g%s-%s_%d' % (element, detector, i), 'Kanal k', 'Counts N')
        prepareGraph(g)
        g.GetXaxis().SetRangeUser(peak[2][0], peak[2][1])
        g.SetMinimum(peak[3][0])
        g.SetMaximum(peak[3][1])
        g.Draw('AP')

        fit = None
        paramnames = []
        if len(peak[0]) == 5:
            fit = Fitter('fit%d' % i, 'pol1(0) + 1/(sqrt(2*pi*[4]^2))*gaus(2)')
            paramnames = ['a', 'b', 'A', 'k_{c}', 's']
        elif len(peak[0]) == 4:
            fit = Fitter('fit%d' % i, '[0] + 1/(sqrt(2*pi*[3]^2))*gaus(1)')
            paramnames = ['a', 'A', 'k_{c}', 's']
        elif len(peak[0]) == 3:
            fit = Fitter('fit%d' % i, '1/(sqrt(2*pi*[2]^2))*gaus(0)')
            paramnames = ['A', 'k_{c}', 's']

        l = None
        if len(peak[0]) > 0:
            for j, param in enumerate(peak[0]):
                fit.setParam(j, paramnames[j], param)
            fit.fit(g, *peak[1])

            fitname = ''
            if len(peak[0]) == 5:
                fitname = 'N(k) = a + b*k + #frac{A}{#sqrt{2#pi*#sigma^{2}}} exp(- #frac{1}{2} (#frac{k-k_{c}}{#sigma})^{2})'
            elif len(peak[0]) == 4:
                fitname = 'N(k) = a + #frac{A}{#sqrt{2#pi*#sigma^{2}}} exp(- #frac{1}{2} (#frac{k-k_{c}}{#sigma})^{2})'
            elif len(peak[0]) == 3:
                fitname = 'N(k) = #frac{A}{#sqrt{2#pi*#sigma^{2}}} exp(- #frac{1}{2} (#frac{k-k_{c}}{#sigma})^{2})'
            fit.saveData('../calc/part3/fit_%s-%s_%02d.txt' % (element, detector, i), 'w')
            results = []
            for j, param in fit.params.iteritems():
                results.append((param['value'], param['error']))
            fitresults.append(results)

            # legend
            l = TLegend(0.675, 0.5, 0.995, 0.85)
            l.SetTextSize(0.025)
            l.AddEntry(g, 'Messwerte', 'p')
            l.AddEntry(fit.function, 'Fit mit', 'l')
            l.AddEntry(0, fitname, '')
            l.AddEntry(0, '', '')
            fit.addParamsToLegend(l, chisquareformat='%.2f')
            l.Draw()

        c.Update()
        if PRINTGRAPHS:
            c.Print('../img/part3/%s-%s_%02d.pdf' % (element, detector, i), 'pdf')
    return fitresults


def getEnergyLitVals(elem):
    litvals = []
    if elem == 'Am':
        litvals.append(59.5)
    elif elem == 'Co':
        litvals.append(122.06)
        litvals.append(136.47)
    return litvals


def makeEnergyGauge(detector, peaks, litvals):
    x, sx = zip(*peaks)
    data = DataErrors.fromLists(x, litvals, sx, [0] * len(x))
    c = TCanvas('c_eg_%s' % detector, '', 1280, 720)
    g = data.makeGraph('g_eg_%s' % detector, 'Kanal k', 'Energie E / eV')
    g.Draw('AP')

    fit = Fitter('f_eg_%s' % detector, 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b')
    fit.fit(g, x[0] - 20, x[-1] + 20)
    fit.saveData('../calc/part3/energygauge_%s.txt' % detector, 'w')

    l = TLegend(0.15, 0.6, 0.4, 0.85)
    l.AddEntry(g, 'Messwerte', 'p')
    l.AddEntry(fit.function, 'Fit mit E(k) = a + b*k', 'l')
    fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.4f', '%.4f')], chisquareformat='%.2f')
    l.Draw()

    c.Update()
    if PRINTGRAPHS:
        c.Print('../img/part3/energygauge_%s.pdf' % detector, 'pdf')


def calcAbsorpProb(params, area):
    A, sA = params[len(params) - 3]  # get Amplitude + error
    C = A / area
    sC = C * sA / A
    return C, sC


def calcAbsorbProbRatio(la, lb):
    a, sa = la
    b, sb = lb
    r = a / b
    sr = r * np.sqrt((sa / a) ** 2 + (sb / b) ** 2)
    return r, sr


def evalPart3():
    detectors = [('CdTe', 23), ('Si', 100)]  # detectors with areas in mm
    elements = ['Am', 'Co']

    absProbs = []
    for det, area in detectors:
        # fits
        fitresults = []
        litvals = []  # literature values for energies of peaks
        for elem in elements:
            fitresults.append(fitSpectrum(det, elem, getParams(det, elem)))
            # add manually peak for Si-Co
            if det == 'Si' and elem == 'Co':
                fitresults.append([loadCSVToList('../calc/part3/fit_Co-Si_01_mergedbins_raw.txt')])
            litvals += getEnergyLitVals(elem)

        # make energy gauge and calculate absorption probabilities
        peaks = []
        sigmas = []
        absProbs_det = []
        for fit in fitresults:
            for peak in fit:
                c, sc = peak[-2]
                sigmas.append(peak[-1])
                peaks.append((c, sc))
                absProbs_det.append(calcAbsorpProb(peak, area))
        makeEnergyGauge(det, peaks, litvals)
        absProbs.append(absProbs_det)
        with TxtFile('../calc/part3/AbsProbs_%s.txt' % det, 'w') as f:
            for i, absProb in enumerate(absProbs_det):
                f.writeline('\t', str(litvals[i]), *map(str, absProb))
        with TxtFile('../calc/part3/RER_%s.txt' % det, 'w') as f:
            RERs = []
            for sigma, peak in zip(sigmas, peaks):
                s, ss = sigma
                p, sp = peak
                RER = 2*np.sqrt(2*np.log(2))*s/ p
                sRER = RER * np.sqrt((ss / s) ** 2 + (sp / p) ** 2)
                RERs.append(RER)
                f.writeline('\t', str(p), str(sp), str(RER), str(sRER))

    # calculate absorption rations for peaks
    detnames = zip(*detectors)[0]
    for i, det1 in enumerate(detnames):
        for j, det2 in enumerate(detnames):
            if not det1 == det2:
                absProbs1 = absProbs[i]
                absProbs2 = absProbs[j]
                with TxtFile('../calc/part3/AbsRatio_%s_%s.txt' % (det1, det2), 'w') as f:
                    for k, lists in enumerate(zip(absProbs1, absProbs2)):
                        f.writeline('\t', str(litvals[k]), *map(str, calcAbsorbProbRatio(*lists)))


def main():
    setupROOT()
    evalPart3()


if __name__ == "__main__":
    main()
