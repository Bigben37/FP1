#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
import os.path
import csv
from data import Data  # make sure to set up your PYTHONPATH variable to find module or copy to same dir


class DataU(Data):

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                xi, yi = row
                self.addPoint(float(xi.replace(',', '.')), float(yi.replace(',', '.')))


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1) 
    gStyle.SetPadTickX(1)
    m = DataU.fromPath("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")  # messurement 
    u = DataU.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")  # underground
    d = m - u  # real data

    # start graphics
    gmax = 4000
    gmin = 0.01

    c = TCanvas('c', '', 800, 600)
    c.SetLogy()
    dg = d.makeGraph('d', 'Spannung U / V', 'Z#ddot{a}hlrate n / (1/s)')
    dg.SetMaximum(gmax)
    dg.SetMinimum(gmin)
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
