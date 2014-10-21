#!/usr/bin/python2.7
from functions import setupROOT  # make sure to add ../lib to your project path or copy file from there
from kernspin import NMRData
from ROOT import TCanvas, TLegend


def main():
    datas = [2, 5, 7, 9]
    for data in datas:
        # get data
        ch1data = NMRData.fromPath('../data/LOCK%02d.CSV' % data)
        ch2data = NMRData.fromPath('../data/LOCK%02d.CSV' % (data + 1))

        # make graphs
        c = TCanvas('c_%d' % data, '', 1280, 720)
        ch1 = ch1data.makeGraph('ch1_%d' % data, 'Zeit t / s', 'Spannung U / V')
        ch1.SetMarkerStyle(1)
        ch1.Draw('AP')
        ch2 = ch2data.makeGraph('ch2_%d' % data, 'Zeit t / s', 'Spannung U / V')
        ch2.SetMarkerStyle(1)
        ch2.SetMarkerColor(2)
        ch2.Draw('P')

        l = TLegend(0.7, 0.875, 0.99, 0.975)
        l.SetTextSize(0.03)
        l.AddEntry(ch1, 'Absorbtionssignal', 'p')
        l.AddEntry(ch2, 'Modulation des Magnetfeldes', 'p')
        l.Draw()

        c.Update()
        c.Print('../img/graph_%02d.pdf' % data, 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()
