#!/usr/bin/python2.7
from ROOT import gROOT, TCanvas, TLegend, TF1, TVirtualFitter, TMatrixD
import os.path
import csv
import numpy
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
    
    l = TLegend(0.55, 0.4, 0.98, 0.7)
    l.AddEntry('du', '{}^{238} Uran ohne Untergrund', 'p')
    l.AddEntry('dk', '{}^{40} Kalium ohne Untergrund', 'p')
    l.SetTextSize(0.035)
    l.Draw()
    
    c.Update()
    c.Print('../img/Kalium40_Charakteristik.pdf', 'pdf')
    
def readSingleEntryFile(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        with open(p, 'rb') as f:
            return float(f.readline().split('\t')[1].replace(',', '.'))

def makeMassFit():
    # config files
    # file = [mass, path]
    files = []
    files.append([2.0123, "../data/11_K_m9_3200_t420.txt", 420])
    files.append([2.0123, "../data/11b_K_m9_3200_t420.txt", 420])
    files.append([1.9047, "../data/13_K_m8_3200_t420.txt", 420])
    files.append([1.6812, "../data/15_K_m7_3200_t420.txt", 420])
    files.append([1.4827, "../data/17_K_m6_3200_t420.txt", 420])
    files.append([1.2952, "../data/19_K_m5_3200_t480.txt", 480])
    files.append([1.0993, "../data/21_K_m4_3200_t480.txt", 480])
    files.append([0.8086, "../data/23_K_m3_3200_t540.txt", 540])
    files.append([0.6954, "../data/25_K_m2_3200_t540.txt", 540])
    files.append([0.5007, "../data/27_K_m1_3200_t660.txt", 660])
    files.append([0.3030, "../data/29_K_m0_3200_t780.txt", 780])
    u = readSingleEntryFile('../data/32b_Untergrund_3200_t36000_corr.txt')
    tu = 36000
    
    d = MassCounts()
    
    for file in files:
        n = readSingleEntryFile(file[1])
        d.addPoint(file[0] , n - u, 0, numpy.sqrt(n / file[2] + u / tu))
       
    c = TCanvas('c2', '', 800, 600)
    g = d.makeGraph('g', 'Massa m / g', 'Z#ddot{a}hlrate n / (1/s)')
    g.Draw('AP')
    
    f = TF1('fitfunc', '[0]*(1-exp(-[1]*x))')
    f.SetParameter(0, 1)
    f.SetParName(0, 'a')
    f.SetParameter(1, 1)
    f.SetParName(1, 'b')
    f.SetLineColor(2)
    f.SetLineWidth(1)
    g.Fit(f, '', '', 0, 2.1)
    print("chi^2 / ndf = ", f.GetChisquare() / f.GetNDF())
    
    fitter = TVirtualFitter.GetFitter()
    matrix = TMatrixD(2, 2, fitter.GetCovarianceMatrix())
    matrix.Print()
    
    c.Update()
    c.Print('../img/Kalium40_MassDepenency.pdf')

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    #makeCharacteristic()
    makeMassFit()
    
    
if __name__ == "__main__":
    main()