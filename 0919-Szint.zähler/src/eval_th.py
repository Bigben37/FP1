#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from szint import SzintData

def evalTh():
    data = SzintData.fromPath('../data/th.TKA')
    data.prepare()
    # TODO use energy gauge
    c = TCanvas('c', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph('g', 'Kanalnummer', 'Z#ddot{a}hlrate / (1/s)')
    g.SetMinimum(1e-5)
    g.SetMarkerStyle(1)
    g.Draw('AP')
    
    #TODO Fits
    
    c.Update()
    c.Print('../img/th_peaks.pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalTh()

if __name__ == "__main__":
    main()