#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas
from I2 import I2Data
from txtfile import TxtFile # make sure to add ../../lib to your project path or copy file from there

def evalHgPeaks():
    data = I2Data.fromPath('../data/02_Hg_full_ngg11.txt')
    mins = data.findExtrema(10, 425, 630, False)
    mins.filterY(1300)
    with TxtFile.fromRelPath('../calc/hg_lines.txt', 'w') as f:
        for min in mins.points:
            f.writeline(str(min[0]))

    c = TCanvas('c1', '', 1280, 720)
    c.SetLogy()
    g = data.makeGraph('g', 'wavelength #lambda / nm', 'intensity / a.u.')
    g.GetXaxis().SetRangeUser(415, 620)
    g.SetMarkerStyle(1)
    g.Draw('AP')

    m = mins.makeGraph()
    if m:
        m.SetMarkerColor(2)
        m.Draw('P')

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