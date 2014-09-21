#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas
from I2 import I2Data

def evalHalogenLamp():
    data = I2Data.fromPath('../data/03_Halogen_ngg10.txt')

    c = TCanvas('c1', '', 1280, 720)
    g = data.makeGraph('g', 'wavelength #lambda / nm', 'intensity / a.u.')
    g.GetXaxis().SetRangeUser(415, 620)
    g.GetYaxis().SetTitleOffset(1.3)
    g.SetMarkerStyle(1)
    g.Draw('AP')

    c.Update()
    c.Print('../img/halogen_lamp.pdf', 'pdf')
    
def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    evalHalogenLamp()

if __name__ == "__main__":
    main()