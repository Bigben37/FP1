#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
import os
import numpy as np
from data import Data, DataErrors  # make sure to add ../lib to your project path or copy file from there
from fitter import Fitter          # make sure to add ../lib to your project path or copy file from there
from txtfile import TxtFile        # make sure to add ../lib to your project path or copy file from there
from lhwz import LHWZData

def makeCharacteristic():
    errorf = lambda n: np.sqrt(n / 50)  # t = 50s
    mk = LHWZData.fromPath("../data/10_K_m9_Zaehlrohrcharakteristik_2500-4000-100.txt")  # kalium
    mk.setYErrorFunc(errorf)
    mu = LHWZData.fromPath("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")  # Uranium
    mu.setYErrorFunc(errorf)
    u  = LHWZData.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")                # underground
    u.setYErrorFunc(errorf)
    du = mu - u
    u.points = u.points[15:]  # get relevant underground (2500V-4000V) for kalium
    dk = mk - u

    c = TCanvas('c1', '', 800, 600)
    c.SetLogy()
    du.setYErrorAbs(0)  # errors to small to see properly -> set to 0
    dug = du.makeGraph('du', 'Spannung U / V', 'Z#ddot{a}hlrate n / (1/s)')
    dug.SetMaximum(4000)
    dug.SetMinimum(1)
    dug.Draw('AP')
    dkg = dk.makeGraph('dk')
    dkg.SetMarkerColor(4)  # blue
    dkg.Draw('P')

    l = TLegend(0.55, 0.4, 0.98, 0.7)
    l.AddEntry('du', '{}^{238} Uran ohne Untergrund', 'p')
    l.AddEntry('dk', '{}^{40} Kalium ohne Untergrund', 'p')
    l.SetTextSize(0.035)
    l.Draw()

    c.Update()
    c.Print('../img/Kalium40_Charakteristik.pdf', 'pdf')


def readSingleEntryFile(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        with open(p, 'rb') as f:
            return float(f.readline().split('\t')[1].replace(',', '.'))


def makeMassFit():
    # config files
    # file = [mass, path]
    files = []
    files.append([2.0123, "../data/11_K_m9_3200_t420.txt", 420])
    files.append([2.0123, "../data/11b_K_m9_3200_t420.txt", 420])
    files.append([1.9047, "../data/13_K_m8_3200_t420.txt", 420])
    files.append([1.6812, "../data/15_K_m7_3200_t420.txt", 420])
    files.append([1.4827, "../data/17_K_m6_3200_t420.txt", 420])
    files.append([1.2952, "../data/19_K_m5_3200_t480.txt", 480])
    files.append([1.0993, "../data/21_K_m4_3200_t480.txt", 480])
    files.append([0.8086, "../data/23_K_m3_3200_t540.txt", 540])
    files.append([0.6954, "../data/25_K_m2_3200_t540.txt", 540])
    files.append([0.5007, "../data/27_K_m1_3200_t660.txt", 660])
    files.append([0.3030, "../data/29_K_m0_3200_t780.txt", 780])
    u = 0.760
    tu = 50

    d = DataErrors()

    for file in files:
        n = readSingleEntryFile(file[1])
        d.addPoint(file[0], n - u, 0.001, np.sqrt(n / file[2] + u / tu))

    d.saveDataToLaTeX(['Masse $m /$g', '$s_m /$g', 'Z\"ahlrate $n / (1/\\text{s})$', '$s_n / (1/\\text{s})$'],
                      ['%.3f', '%.3f', '%.3f', '%.3f'], 
                      'Z\"ahlraten von \\kalium\,f\"ur verschiedene Massen mit Fehlern', 'tab:data:kalium', '../src/data_kalium.tex', 'w')

    c = TCanvas('c2', '', 800, 600)
    g = d.makeGraph('g', 'Masse m / g', 'Z#ddot{a}hlrate n / (1/s)')
    g.SetMaximum(6)
    g.SetMinimum(2)
    g.Draw('AP')

    fit = Fitter('f', '[0]*(1-exp(-[1]*x))')
    fit.setParam(0, 'a')
    fit.setParam(1, 'b')
    fit.fit(g, 0.1, 2.5)
    fit.saveData('../fit/kalium.txt')
    
    a = fit.params[0]['value']
    sa = fit.params[0]['error']
    b = fit.params[1]['value']
    sb = fit.params[1]['error']

    l = TLegend(0.4, 0.15, 0.85, 0.5)
    l.AddEntry('g', '{}^{40} Kalium ohne Untergrund', 'p')  # TODO with error bar? (options +'e')
    l.AddEntry(fit.function, 'Fit mit n(m)=a(1-exp(-b*m))', 'l')
    l.AddEntry(0, '#chi^{2} / DoF : %f' % fit.getChisquareOverDoF(), '')
    l.AddEntry(0, 'Paramter:', '') 
    l.AddEntry(0, 'a: %e #pm %e' % (a, sa), '')
    l.AddEntry(0, 'b: %e #pm %e' % (b, sb), '')   
    l.SetTextSize(0.03)
    l.Draw()

    NA = 6.02214129e23
    hrel = 0.000118
    mrel = 39.0983 + 35.45
    f = 1.29
    rho = fit.getCorrMatrixElem(1, 0)
    thalf = (np.log(2) * NA * hrel * f) / (1.12 * mrel * 2 * a * b) / (3600 * 24 * 365.242)
    sthalf = thalf * np.sqrt((sa / a) ** 2 + (sb / b) ** 2 + 2 * rho * (sa / a) * (sb / b))

    with TxtFile.fromRelPath('../fit/kalium.txt', 'a') as f:
        f.writeline()
        f.writeline('calculations')
        f.writeline('============')
        f.writeline('\t', 'half-life of Kalium:', '%e' % thalf, TxtFile.PM, '%e' % sthalf)

    c.Update()
    c.Print('../img/Kalium40_Massenabhaengigkeit.pdf')

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    makeCharacteristic()
    makeMassFit()

if __name__ == "__main__":
    main()
