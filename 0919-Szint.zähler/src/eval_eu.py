#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData

def evalEu():
    data = SzintData.fromPath('../data/eu.TKA')
    # TODO underground
    c = TCanvas('c', '', 1280, 720)
    #c.SetLogy()
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.Draw('AP')
    c.Update()
    c.Print('../img/eu_peaks.pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalEu()

if __name__ == "__main__":
    main()