#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from I2 import I2Data
from txtfile import TxtFile

def getMinima():
    data = I2Data.fromPath('../data/04_I2_ngg10_10ms.txt')
    mins = data.findExtrema(5, 508, 620)
    with TxtFile.fromRelPath('../calc/I2_absorption.txt', 'w') as f:
        for min in mins.points:
            f.writeline('%.2f' % min[0])

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph()
    g.SetMarkerStyle(1)
    g.GetXaxis().SetRangeUser(505, 620)
    g.SetMinimum(18000)
    g.SetMaximum(49000)
    g.Draw('AP')

    m = mins.makeGraph()
    m.SetMarkerColor(2)
    m.Draw('P')

    c.Update()
    c.Print('../img/I2_absorption.pdf', 'pdf')

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    getMinima()

if __name__ == "__main__":
    main()