#!/usr/bin/python2.7
from ROOT import TCanvas, TLegend

# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from data import Data
from functions import setupROOT, loadCSVToList
# ========================================================================


def main():
    data = loadCSVToList('../data/141022/squid_pattern_HM1508-2.csv', ',')
    xlist, y1list, y2list, temp = zip(*data)

    uSquid = Data.fromLists(xlist, y1list)
    uRef = Data.fromLists(xlist, y2list)
    uRef.multiplyY(0.1)

    c = TCanvas('c', '', 1280, 720)
    gSquid = uSquid.makeGraph('gSquid', 'Zeit t / s', 'Spannung U / V')
    gSquid.SetMarkerStyle(1)
    gRef = uRef.makeGraph('gRef')
    gRef.SetMarkerStyle(1)
    gRef.SetMarkerColor(2)

    gSquid.GetXaxis().SetLimits(0, 0.2)
    gSquid.Draw('AP')
    gRef.Draw('P')

    l = TLegend(0.725, 0.85, 0.99, 0.99)
    l.SetTextSize(0.03)
    l.AddEntry(gSquid, 'Spannung am SQUID', 'p')
    l.AddEntry(gRef, 'Spannung am Funktions-', 'p')
    l.AddEntry(0, 'generator (mit Faktor 0.1)', '')
    l.Draw()

    c.Update()
    c.Print('../img/pattern.pdf', 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()
