#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from I2 import I2Data

def evalNaMainPeak():
    data = I2Data.fromPath('../data/01_Na_ngg13.txt')
    mins = data.findExtrema(200, 508, 630, False)
    mins.filterY(1400)
    print(mins.points)

    c = TCanvas('c1', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('AP')

    m = mins.makeGraph()
    if m:
        m.SetMarkerColor(2)
        m.Draw('P')

    c.Update()
    c.Print('../img/NaMainPeak.pdf', 'pdf')
    
def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalNaMainPeak()

if __name__ == "__main__":
    main()