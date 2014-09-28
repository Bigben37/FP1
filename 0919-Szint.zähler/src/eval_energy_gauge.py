#!/usr/bin/python2.7
import os
from ROOT import gROOT, gStyle, TCanvas, TLegend
from data import DataErrors
from fitter import Fitter
from txtfile import TxtFile

def loadCSVToList(path, delimiter='\t'):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        data = []
        with open(p, 'r') as f:
            for line in f:
                data.append(list(map(lambda x: float(x), line.strip().split(delimiter))))  # remove \n, split by delimiter, convert to float
        return data
    
        
def evalEnergyGauge():
    datalist  = loadCSVToList('../calc/energy_na.txt')
    datalist += loadCSVToList('../calc/energy_co.txt')
    datalist += loadCSVToList('../calc/energy_eu.txt')
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
    fit.saveData('../calc/energy_gauge.txt', 'w')
    
    #write raw data for reuse
    with TxtFile('../calc/energy_gauge_raw.txt', 'w') as f:
        f.writeline('\t', str(fit.params[0]['value']), str(fit.params[0]['error']))
        f.writeline('\t', str(fit.params[1]['value']), str(fit.params[1]['error']))
        f.writeline(str(fit.getCorrMatrixElem(0, 1)))
    
    c.Update()
    c.Print('../img/energy_gauge.pdf', 'pdf')
        

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalEnergyGauge()

if __name__ == "__main__":
    main()