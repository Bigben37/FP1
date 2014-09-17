#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from I2 import I2Data

def evalHgPeaks():
    data = I2Data.fromPath('../data/02_Hg_full_ngg11.txt')
    mins = data.findExtrema(100, 425, 630, False)
    mins.filterY(1300)
    print('found %d peaks' % mins.getLength())
    
    #TODO save peak data

    c = TCanvas('c1', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('AP')

    m = mins.makeGraph()
    if m:
        m.SetMarkerColor(2)
        m.Draw('P')
        
    #TODO Legend

    c.Update()
    c.Print('../img/HgPeaks.pdf', 'pdf')
    
def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalHgPeaks()

if __name__ == "__main__":
    main()