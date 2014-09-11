#!/usr/bin/python2.7
from ROOT import gROOT, TCanvas, TLegend
import os.path
import csv
from data import Data, DataErrors  # make sure to set up your PYTHONPATH variable to find module or copy to same dir

class DataK(Data):

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                xi, yi = row
                self.addPoint(float(xi.replace(',', '.')), float(yi.replace(',', '.')))


class MassCounts(DataErrors):                
    def loadY(self, x, path):
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        with open(p, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                buf, y = row
                self.addPoint(x, float(yi.replace(',', '.')))        
                

def makeCharacteristic():
    mk = DataK.fromPath("../data/10_K_m9_Zaehlrohrcharakteristik_2500-4000-100.txt")  # kalium
    mu = DataK.fromPath("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt")  # Uranium
    u = DataK.fromPath("../data/02_Uran_Untergrund_1000-4000-100.txt")                # underground
    du = mu - u
    u.points = u.points[15:]  # get relevant underground (2500V-4000V) for kalium
    dk = mk - u
    
    # start graphics
    gmax = 4000
    gmin = 1
    
    c = TCanvas('c1', '', 800, 600)
    c.SetLogy()
    dug = du.makeGraph('du', 'Spannung U / V', 'Z#ddot{a}hlrate n / (1/s)')
    dug.SetMaximum(gmax)
    dug.SetMinimum(gmin)
    dug.Draw('AP')
    dkg = dk.makeGraph('dk')
    dkg.SetMarkerColor(4)  # blue
    dkg.Draw('P')
    
    l = TLegend(0.65, 0.5, 0.89, 0.7)
    l.AddEntry('du', '{}^{238} Uran', 'p')
    l.AddEntry('dk', '{}^{40} Kalium', 'p')
    l.SetTextSize(0.05)
    l.Draw()
    
    c.Update()
    c.Print('../img/Kalium40_Charakteristik.pdf', 'pdf')
    

def makeMassFit():
    pass

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    makeCharacteristic()
    makeMassFit()
    
    
if __name__ == "__main__":
    main()