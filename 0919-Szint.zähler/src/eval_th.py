#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend, TF1
from szint import SzintData
from fitter import Fitter


def evalTh():
    data = SzintData.fromPath('../data/th.TKA')
    data.prepare()
    c = TCanvas('c', '', 1280, 720)
    # c.SetLogy()
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMarkerStyle(1)
    g.SetMinimum(0)
    g.GetXaxis().SetRangeUser(0, 1200)
    g.Draw('AP')

    # start values for single peak fit
    peaks = []
    peaks.append([[(0, 'a0', 0.1), (1, 'b0', 0), (2, 'A0', 1),    (3, 'c0', 225),  (4, 's0', 20)], 190, 300])
    peaks.append([[(0, 'a1', 0.1), (1, 'b1', 0), (2, 'A1', 0.3),  (3, 'c1', 410),  (4, 's1', 20)], 350, 450])
    peaks.append([[(0, 'a2', 0.3), (1, 'b2', 0), (2, 'A2', 0.2),  (3, 'c2', 625),  (4, 's2', 30)], 575, 640])
    peaks.append([[(0, 'a3', 0.1), (1, 'b3', 0), (2, 'A3', 0.75), (3, 'c3', 700),  (4, 's3', 20)], 650, 775])
    peaks.append([[(0, 'a4', 0.1), (1, 'b4', 0), (2, 'A4', 0.5),  (3, 'c4', 900),  (4, 's4', 20)], 800, 950])
    peaks.append([[(0, 'a5', 0.1), (1, 'b5', 0), (2, 'A5', 0.25), (3, 'c5', 1050), (4, 's5', 30)], 1000, 1100])

    # fit single peaks and get exact values for multi-peak fit
    params = []
    for i, peak in enumerate(peaks):
        fit = Fitter('fit%d' % i, 'pol1(0) + gaus(2)')
        fit.function.SetLineColor(i + 2)
        for param in peak[0]:
            fit.setParam(*param)
        fit.fit(g, peak[1], peak[2])
        params.append([fit.params[2]['value'], fit.params[3]['value'], fit.params[4]['value']])
        #if i == 5:
        for j, par in fit.params.iteritems():
            print(par['name'], par['value'])
        print('')

    # make multi-peak fit
    fit = Fitter('f', 'pol2(0) + gaus(3) + gaus(6) + gaus(9) + gaus(12) + gaus(15) + gaus(18)')
    fit.function.SetNpx(10000)
    fit.setParam(0, 'a', 0.1)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'c', 0)
    for i, param in enumerate(params):
        fit.setParam(3 * (i + 1) + 0, 'A%d' % (i + 1), param[0])
        fit.setParam(3 * (i + 1) + 1, 'c%d' % (i + 1), param[1])
        fit.setParam(3 * (i + 1) + 2, 's%d' % (i + 1), param[2])
    fit.fit(g, 190, 1150)
    fit.saveData('../calc/th_peaks.txt', 'w')

    c.Update()
    c.Print('../img/th_peaks.pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalTh()

if __name__ == "__main__":
    main()
