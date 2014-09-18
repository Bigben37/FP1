#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from I2 import I2Data
from txtfile import TxtFile

def evalNaPeaks():
    data = I2Data.fromPath('../data/01_Na_ngg13.txt')
    mins = data.findExtrema(200, 508, 630, False)
    mins.filterY(1400)
    with TxtFile.fromRelPath('../calc/na_lines.txt', 'w') as f:
        for min in mins.points:
            f.writeline(str(min[0]))

    c = TCanvas('c1', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('AP')
    
    #TODO Legend

    m = mins.makeGraph()
    if m:
        m.SetMarkerColor(2)
        m.Draw('P')

    c.Update()
    c.Print('../img/NaPeaks.pdf', 'pdf')
    
def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalNaPeaks()

if __name__ == "__main__":
    main()