#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
import os.path
import numpy as np
from lhwz import LHWZData
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there
from fitter import Fitter    # make sure to add ../lib to your project path or copy file from there
from txtfile import TxtFile  # make sure to add ../lib to your project path or copy file from there

def makeCharacteristic():
    errorf = lambda n: np.sqrt(n / 50)  # t = 50s
    msm = LHWZData.fromPath("../data/07_Sm_ggrFl_Zaehlrohrcharakteristik_1000-2200-100.txt")  # Samarium
    msm.setYErrorFunc(errorf)
    mu = LHWZData.fromPath("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")       # Uranium
    mu.setYErrorFunc(errorf)
    u = LHWZData.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")                     # underground
    u.setYErrorFunc(errorf)
    du = mu - u
    u.points = u.points[:13]  # get relevant underground (1000V-2200V) for samarium
    dsm = msm - u

    c = TCanvas('c1', '', 800, 600)
    c.SetLogy()
    du.setYErrorAbs(0)  # errors to small to see properly -> set to 0
    dug = du.makeGraph('du', 'Spannung U / V', 'Z#ddot{a}hlrate n / (1/s)')
    dug.SetMaximum(4000)
    dug.SetMinimum(0.1)
    dug.Draw('AP')
    dsmg = dsm.makeGraph('dsm')
    dsmg.SetMarkerColor(4)  # blue
    dsmg.Draw('P')

    l = TLegend(0.55, 0.4, 0.98, 0.7)
    l.AddEntry('du', '{}^{238} Uran ohne Untergrund', 'p')
    l.AddEntry('dsm', '{}^{147} Samarium ohne Untergrund', 'p')
    l.SetTextSize(0.03)
    l.Draw()

    c.Update()
    c.Print('../img/Samarium147_Charakteristik.pdf', 'pdf')

def readSingleEntryFile(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        with open(p, 'r') as f:
            return float(f.readline().split('\t')[1].replace(',', '.'))

def avgstd(list):
    return np.average(list), np.std(list, ddof=1)

def area(*args):
    d  = args[0][0]
    sd = args[0][1]
    return np.pi*(d/2)**2, (d / 2)*np.pi*sd

def calculateHalfLife(a, n, sa, sn):
    c  = 0.004025
    NA = 6.02214129e23
    m  = 2*150.36 + 3*15.999
    h = 0.1487
    t = (np.log(2)*c*NA*h*a) / (2 * m * n) / (3600 * 24 * 365.242)
    st = t * np.sqrt((sa / a)**2 + (sn/n)**2)
    return t, st

def makeAreaFit():
    # calculate ares
    d_s = [1.000, 0.990, 0.990, 1.005, 1.000, 1.005]
    d_m = [1.700, 1.690, 1.695, 1.700, 1.705, 1.705]
    d_l = [2.880, 2.880, 2.875, 2.880, 2.880, 2.880]
    d = map(avgstd, [d_s, d_m, d_l])
    a = map(area, d)
    
    diaarea = DataErrors()
    for i in range(3):
        diaarea.addPoint(d[i][0], a[i][0], d[i][1], a[i][1])
    diaarea.saveDataToLaTeX(['Durchmesser $d$ / cm', '$s_d$ / cm', 'Fl\"ache $F / \\text{cm}^2$', '$s_F / \\text{cm}^2$'], 
                            ['%.4f', '%.4f', '%.4f', '%.4f'], 'Verschiedene Fl\"achen f\"ur die Samariummessung', 
                            'tab:data:samarium:area', '../src/data_samarium_areas.tex', 'w')
    
    with TxtFile('../fit/samarium.txt', 'w') as f:
        f.writeline('areas')
        f.writeline('=====')
        for b in a:
            f.writeline('\t', '%e' % b[0], TxtFile.PM, '%e' % b[1])
        f.writeline()
    
    
    #read data from files
    #file=[area, area error, path, time]
    files = []
    files.append([a[0][0], a[0][1], '../data/31_Sm_kl_1600_t3000.txt', 3000])
    files.append([a[1][0], a[1][1], '../data/34_Sm_m_1600_t2400.txt', 2400])
    files.append([a[2][0], a[2][1], '../data/08_Sm_ggrFl_1600-1600-0.txt', 1200])
    u = readSingleEntryFile('../data/09_Untergrund_1600-1600-0.txt') 
    tu = 3600
    d = DataErrors()
    for file in files:
        n = readSingleEntryFile(file[2])
        d.addPoint(file[0], n - u, file[1], np.sqrt(n / file[3] + u / tu))
        
    d.saveDataToLaTeX(['Fl\"ache $F / \\text{cm}^2$', '$s_F / \\text{cm}^2$', 'Z\"ahlrate $n / (1/\\text{s})$', '$s_n / (1/\\text{s})$'], 
                      ['%.4f', '%.4f', '%.3f', '%.3f'], 'Z\"ahlraten von \\samarium~f\"ur verschiedene Fl\"achen mit Fehlern', 
                      'tab:data:samarium', '../src/data_samarium.tex', 'w')
        
    c = TCanvas('c2', '', 800, 600)
    g = d.makeGraph('g', 'Fl#ddot{a}che F / cm^{2}', 'Z#ddot{a}hlrate n / (1/s)')
    g.Draw('AP')
    
    fit = Fitter('f', '[0]+[1]*x')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 0.05)
    fit.fit(g, 0, 30)
    fit.saveData('../fit/samarium.txt', 'a')
    
    a = fit.params[0]['value']
    sa = fit.params[0]['error']
    b = fit.params[1]['value']
    sb = fit.params[1]['error']

    l = TLegend(0.55, 0.15, 0.98, 0.5)
    l.AddEntry('g', '{}^{147} Samarium ohne Untergrund', 'p')  # TODO with error bar? (options +'e')
    l.AddEntry(fit.function, 'Fit mit n(F)=a+b*F', 'l')
    l.AddEntry(0, '#chi^{2} / DoF : %f' % fit.getChisquareOverDoF(), '')
    l.AddEntry(0, 'Paramter:', '') 
    l.AddEntry(0, 'a: %e #pm %e' % (a, sa), '')
    l.AddEntry(0, 'b: %e #pm %e' % (b, sb), '')   
    l.SetTextSize(0.03)
    l.Draw()
    
    c.Update()
    c.Print('../img/Samarium147-Flaechenabhaengigkeit.pdf', 'pdf')
    
    #calculation with fit parameters
    c  = 0.004025
    NA = 6.02214129e23
    m  = 2*150.36 + 3*15.999
    h = 0.1487
    t = (np.log(2) * c * NA * h) / (2 * m * b) / (3600 * 24 * 365.242)
    st = t * (sb / b)
    with TxtFile('../fit/samarium.txt', 'a') as f:
        f.writeline('calculation from fit')
        f.writeline('====================')
        f.writeline('\t', '%e' % t, TxtFile.PM, '%e' % st)
        f.writeline()
    
    # calculation from single data points
    sc = map(lambda p: calculateHalfLife(*p), d.points)
    with TxtFile('../fit/samarium.txt', 'a') as f:
        f.writeline('calculation from single data points')
        f.writeline('===================================')
        for s in sc:
            f.writeline('\t', '%e' % s[0], TxtFile.PM, '%e' % s[1])
        f.writeline()
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    makeCharacteristic()
    makeAreaFit()

if __name__ == "__main__":
    main()
