#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
import os.path
import csv
from data import Data  # make sure to set up your PYTHONPATH variable to find module or copy to same dir


class DataSm(Data):

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                xi, yi = row
                self.addPoint(float(xi.replace(',', '.')), float(yi.replace(',', '.')))


def makeCharacteristic():
    msm = DataSm.fromPath("../data/07_Sm_ggrFl_Zaehlrohrcharakteristik_1000-2200-100.txt")  # Samarium
    mu = DataSm.fromPath("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")       # Uranium
    u = DataSm.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")                     # underground
    du = mu - u
    u.points = u.points[:13]  # get relevant underground (1000V-2200V) for samarium
    dsm = msm - u

    c = TCanvas('c1', '', 800, 600)
    c.SetLogy()
    dug = du.makeGraph('du', 'Spannung U / V', 'Z#ddot{a}hlrate n / (1/s)')
    dug.SetMaximum(4000)
    dug.SetMinimum(0.1)
    dug.Draw('AP')
    dsmg = dsm.makeGraph('dsm')
    dsmg.SetMarkerColor(4)  # blue
    dsmg.Draw('P')

    l = TLegend(0.55, 0.4, 0.98, 0.7)
    l.AddEntry('du', '{}^{238} Uran ohne Untergrund', 'p')
    l.AddEntry('dsm', '{}^{147} Samarium ohne Untergrund', 'p')
    l.SetTextSize(0.03)
    l.Draw()

    c.Update()
    c.Print('../img/Samarium147_Charakteristik.pdf', 'pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    makeCharacteristic()
    # TODO eval areas


if __name__ == "__main__":
    main()
