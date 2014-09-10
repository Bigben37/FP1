#!/usr/bin/python2.7
from ROOT import gROOT, TCanvas, TGraph, TLegend
import os.path
import csv
import array


class Data(object):

    def __init__(self):
        self.path = ''
        self.x = []
        self.y = []

    @staticmethod
    def fromPath(path):
        data = Data()
        data.path = path
        if path:
            data.loadData()
        return data

    @staticmethod
    def fromLists(x, y):
        if len(x) == len(y):
            data = Data()
            data.x = x
            data.y = y
            return data
        else:
            print('Data.fromLists():ERROR - lists have to be the same length')
            return None

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                xi, yi = row
                self.x.append(float(xi.replace(',', '.')))
                self.y.append(float(yi.replace(',', '.').replace(',', '.')))

    def makeGraph(self, name='', xtitle='', ytitle=''):
        graph = TGraph(
            len(self.x), array.array('f', self.x), array.array('f', self.y))
        graph.SetName(name)
        graph.SetMarkerColor(1)
        graph.SetMarkerStyle(5)
        graph.SetTitle("")
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle(ytitle)
        graph.GetYaxis().CenterTitle()
        return graph

    def __add__(self, other):
        if isinstance(other, Data):
            if len(self.y) == len(other.y):
                y = []
                for i in range(len(self.y)):
                    y.append(self.y[i] + other.y[i])
                return Data.fromLists(self.x, y)
            else:
                return NotImplemented
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Data):
            if len(self.y) == len(other.y):
                y = []
                for i in range(len(self.y)):
                    y.append(self.y[i] + other.y[i])
                return Data.fromLists(self.x, y)
            else:
                return NotImplemented
        else:
            return NotImplemented


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    m = Data.fromPath(
        "../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")  # messurement
    # underground
    u = Data.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")
    # real data
    d = m - u

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
