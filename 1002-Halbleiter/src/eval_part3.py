#!/usr/bin/python2.7
from functions import setupROOT
from halbleiter import P3SemiCon, prepareGraph
from ROOT import TCanvas, TLegend, TF1
from fitter import Fitter


def getParamsAmCdTe():
    params = []
    params.append([(0, 0, 500, 285, 25), (260, 310), (200, 350), (0, 560)])
    return params


def getParamsAmSi():
    params = []
    params.append([(0, 0, 50, 300, 25), (260, 330), (250, 340), (0, 60)])
    return params


def getParamsCoCdTe():
    params = []
    params.append([(70, 0, 200, 600, 20), (580, 620), (560, 630), (0, 280)])
    params.append([(20, 675, 40), (640, 700), (620, 720), (0, 30)])
    return params


def getParamsCoSi():
    params = []
    params.append([(0, 0, 20, 600, 20), (580, 650), (570, 660), (0, 30)])
    params.append([(), (670, 710), (650, 750), (0, 3)])
    return params


def printTotalSpectrum(data, element, detector, logy=True):
    c = TCanvas('total_%s-%s' % (element, detector), '', 1280, 720)
    c.SetLogy(logy)
    g = data.makeGraph('g%s-%s' % (element, detector), 'Kanal k', 'Counts N')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 2500)
    g.Draw('APX')
    c.Update()
    c.Print('../img/part3/%s-%s_spectrum.pdf' % (element, detector), 'pdf')


def fitSpectrum(element, detector, params, logy=True):
    data = P3SemiCon.fromPath('../data/part3/%s-%s.mca' % (element, detector))
    printTotalSpectrum(data, element, detector, logy)

    if params:
        for i, peak in enumerate(params):
            c = TCanvas('cpeakl_%s-%s_%d' % (element, detector, i))
            g = data.makeGraph('g%s-%s_%d' % (element, detector, i), 'Kanal k', 'Counts N')
            prepareGraph(g)
            g.GetXaxis().SetRangeUser(peak[2][0], peak[2][1])
            g.SetMinimum(peak[3][0])
            g.SetMaximum(peak[3][1])
            g.Draw('AP')

            fit = None
            paramnames = []
            if len(peak[0]) == 5:
                fit = Fitter('fit%d' % i, 'pol1(0) + gaus(2)')
                paramnames = ['a', 'b', 'A', 'c', 's']
            elif len(peak[0]) == 4:
                fit = Fitter('fit%d' % i, '[0] + gaus(1)')
                paramnames = ['a', 'A', 'c', 's']
            elif len(peak[0]) == 3:
                fit = Fitter('fit%d' % i, 'gaus(0)')
                paramnames = ['A', 'c', 's']

            if len(peak[0]) > 0:
                for j, param in enumerate(peak[0]):
                    fit.setParam(j, paramnames[j], param)
                fit.fit(g, *peak[1])
                fit.saveData('../calc/part3/fit_%s-%s_%02d.txt' % (element, detector, i), 'w')

            """
            f = TF1('f', 'pol1(0)', peak[1][0], peak[1][1])
            f.SetParameter(0, fit.params[0]['value'])
            f.SetParameter(1, fit.params[1]['value'])
            f.Draw('SAME')"""

            c.Update()
            c.Print('../img/part3/%s-%s_%02d.pdf' % (element, detector, i), 'pdf')


def evalPart3():
    #fitSpectrum('Am', 'CdTe', getParamsAmCdTe())
    #fitSpectrum('Am', 'Si', getParamsAmSi())
    fitSpectrum('Co', 'CdTe', getParamsCoCdTe())
    #fitSpectrum('Co', 'Si', getParamsCoSi())


def main():
    setupROOT()
    evalPart3()


if __name__ == "__main__":
    main()
