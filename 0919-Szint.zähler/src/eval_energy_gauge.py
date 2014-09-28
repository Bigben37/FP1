#!/usr/bin/python2.7
import os
from ROOT import gROOT, gStyle, TCanvas, TLegend
from data import DataErrors
from fitter import Fitter
from txtfile import TxtFile
import functions as funcs
    
        
def evalEnergyGauge():
    datalist  = funcs.loadCSVToList('../calc/energy_na.txt')
    datalist += funcs.loadCSVToList('../calc/energy_co.txt')
    datalist += funcs.loadCSVToList('../calc/energy_eu.txt')
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
    # TODO Legend
    c.Update()
    c.Print('../img/energy_gauge_lin.pdf', 'pdf')
    
    fit2 = Fitter('f', 'pol2(0)')
    fit2.function.SetNpx(1000)
    fit2.function.SetLineColor(4)
    fit2.setParam(0, 'a', 0)
    fit2.setParam(1, 'b', fit.params[1]['value'])
    fit2.setParam(2, 'c', 0)
    fit2.fit(g, 0, 3500)
    fit2.saveData('../calc/energy_gauge_lin.txt')
    # TODO Legend
    c.Update()
    c.Print('../img/energy_gauge_quad.pdf', 'pdf')
    
    #write raw data for reuse
    with TxtFile('../calc/energy_gauge_raw.txt', 'w') as f:
        f.writeline('\t', str(fit.params[0]['value']), str(fit.params[0]['error']))
        f.writeline('\t', str(fit.params[1]['value']), str(fit.params[1]['error']))
        f.writeline(str(fit.getCorrMatrixElem(0, 1)))
        

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalEnergyGauge()

if __name__ == "__main__":
    main()