#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from lhwz import LHWZData

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1) 
    gStyle.SetPadTickX(1)
    m = LHWZData.fromPath("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")  # messurement 
    u = LHWZData.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")  # underground
    d = m - u  # real data

    # start graphics
    c = TCanvas('c', '', 800, 600)
    c.SetLogy()
    dg = d.makeGraph('d', 'Spannung U / V', 'Z#ddot{a}hlrate n / (1/s)')
    dg.SetMaximum(4000)
    dg.SetMinimum(0.01)
    dg.Draw('AP')
    ug = u.makeGraph('u')
    ug.SetMarkerColor(4)  # blue
    ug.Draw('P')

    l = TLegend(0.54, 0.6, 0.98, 0.75)
    l.AddEntry('d', '{}^{238} Uran ohne Untergrund ', 'p')
    l.AddEntry('u', 'Untergrund', 'p')
    l.Draw()

    c.Update()
    c.Print('../img/Uran238_Charakteristik.pdf', 'pdf')

if __name__ == "__main__":
    main()
