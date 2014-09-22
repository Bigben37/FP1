#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData

def evalNa():
    data = SzintData.fromPath('../data/th.TKA')
    # TODO underground
    # TODO use energy gauge
    c = TCanvas('c', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph()
    g.SetMinimum(10)
    g.SetMarkerStyle(1)
    g.Draw('AP')
    c.Update()
    c.Print('../img/th_peaks.pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalNa()

if __name__ == "__main__":
    main()