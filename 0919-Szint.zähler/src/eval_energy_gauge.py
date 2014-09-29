#!/usr/bin/python2.7
import os
from ROOT import gROOT, gStyle, TCanvas, TLegend
from data import DataErrors
from fitter import Fitter
from txtfile import TxtFile
import functions as funcs
    
        
def evalEnergyGauge():
    # get data
    datalist  = funcs.loadCSVToList('../calc/energy_na.txt')
    datalist += funcs.loadCSVToList('../calc/energy_co.txt')
    datalist += funcs.loadCSVToList('../calc/energy_eu.txt')
    
    #make latex table
    elems = ['Na', 'Na', 'Co', 'Co', 'Eu', 'Eu']
    with TxtFile('../src/energygauge.tex', 'w') as f:
        f.write2DArrayToLatexTable(zip(*([elems] + zip(*datalist))), ['Element', 'Literaturwert / keV', 'Kanal', 'Fehler auf Kanal'], 
                                   ['%s', '%.0f', '%.2f', '%.2f'], 'Referenzpeaks mit Literaturwerten', 'tab:energygauge')
    
    #convert do DataErrors
    datalist = zip(*datalist)
    data = DataErrors.fromLists(datalist[1], datalist[0], datalist[2], [0] * len(datalist[0]))
    
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanalnummer', 'Energie / keV')
    g.GetXaxis().SetRangeUser(0, 3500)
    g.Draw('AP')
    
    fit = Fitter('f', 'pol1(0)')
    fit.function.SetNpx(1000)
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 0.4)
    fit.fit(g, 0, 3500)
    fit.saveData('../calc/energy_gauge_lin.txt', 'w')
    
    l = TLegend(0.15, 0.6, 0.5, 0.85)
    l.AddEntry('g', 'Referenzpeaks', 'p')
    l.AddEntry(fit.function, 'Fit mit y = a + b*x', 'l')
    l.AddEntry(0, '#chi^{2} / DoF : %.0f' % fit.getChisquareOverDoF(), '')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'a = %.2f #pm %.2f' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.AddEntry(0, 'b = %.5f #pm %.5f' % (fit.params[1]['value'], fit.params[1]['error']), '')
    l.Draw()

    c.Update()
    c.Print('../img/energy_gauge_lin.pdf', 'pdf')
    
    fit2 = Fitter('f', 'pol2(0)')
    fit2.function.SetNpx(1000)
    fit2.setParam(0, 'a', 0)
    fit2.setParam(1, 'b', fit.params[1]['value'])
    fit2.setParam(2, 'c', 0)
    fit2.fit(g, 0, 3500)
    fit2.saveData('../calc/energy_gauge_lin.txt')
    
    l = TLegend(0.15, 0.575, 0.5, 0.85)
    l.AddEntry('g', 'Referenzpeaks', 'p')
    l.AddEntry(fit2.function, 'Fit mit y = a + b*x + c*x^2', 'l')
    l.AddEntry(0, '#chi^{2} / DoF : %.0f' % fit2.getChisquareOverDoF(), '')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'a = %.2f #pm %.2f' % (fit2.params[0]['value'], fit2.params[0]['error']), '')
    l.AddEntry(0, 'b = %.5f #pm %.5f' % (fit2.params[1]['value'], fit2.params[1]['error']), '')
    l.AddEntry(0, 'c = %.8f #pm %.8f' % (fit2.params[2]['value'], fit2.params[2]['error']), '')
    l.Draw()
    
    c.Update()
    c.Print('../img/energy_gauge_quad.pdf', 'pdf')
    
    #write raw data for reuse
    with TxtFile('../calc/energy_gauge_raw.txt', 'w') as f:
        f.writeline('\t', str(fit2.params[0]['value']), str(fit2.params[0]['error']))
        f.writeline('\t', str(fit2.params[1]['value']), str(fit2.params[1]['error']))
        f.writeline('\t', str(fit2.params[2]['value']), str(fit2.params[2]['error']))
        f.writeline(str(fit2.getCorrMatrixElem(0, 1))) #a, b
        f.writeline(str(fit2.getCorrMatrixElem(0, 2))) #a, c
        f.writeline(str(fit2.getCorrMatrixElem(1, 2))) #b, c
        

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalEnergyGauge()

if __name__ == "__main__":
    main()