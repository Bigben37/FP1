from farpock import PockData
from fitter import Fitter
from ROOT import gROOT, gStyle, TCanvas, TLegend
from functions import avgerrors
import numpy as np
from txtfile import TxtFile
from data import DataErrors

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    
    eval()
          
   

def eval():
    
  
    data1 = PockData.fromPath('../data/%s.tab' % 'pock_gleich_01', 2)
    data2 = PockData.fromPath('../data/%s.tab' % 'pock_gleich_02', 2)
    data3 = PockData.fromPath('../data/%s.tab' % 'pock_gleich_03', 2)
    data4 = PockData.fromPath('../data/%s.tab' % 'pock_gleich_01', 1)
    
    L0 = [0]*data1.getLength()
    Ly1 = [0.41]*data1.getLength()
    Ly2 = [0.31]*data1.getLength()
    Ly3 = [0.14]*data1.getLength()
    Ly4 = [0]*data1.getLength()
    
    Offset1 = DataErrors.fromLists(L0, Ly1, L0, L0)
    Offset2 = DataErrors.fromLists(L0, Ly2, L0, L0)
    Offset3 = DataErrors.fromLists(L0, Ly3, L0, L0)
    Offset4 = DataErrors.fromLists(L0, Ly4, L0, L0)
    
    data1 += Offset1
    data2 += Offset2
    data3 += Offset3
    data4 += Offset4
  
  
    
    c = TCanvas('c', '', 1280, 720)
    
    g1 = data1.makeGraph('g1', 'Zeit t / s', 'Spannung U / V')
    g1.SetMarkerStyle(8)
    g1.SetMarkerSize(0.5)
    g1.SetMarkerColor(65)
    g1.GetXaxis().SetRangeUser(0, 0.005)
    g1.SetMinimum(-0.08)
    g1.SetMaximum(0.45)
    g1.Draw('AP')
    
    g2 = data2.makeGraph('g2', 'Zeit t / s', 'Spannung U / V')
    g2.SetMarkerStyle(8)
    g2.SetMarkerSize(0.5)
    g2.SetMarkerColor(60)
    g2.Draw('P')
    
    g3 = data3.makeGraph('g3', 'Zeit t / s', 'Spannung U / V')
    g3.SetMarkerStyle(8)
    g3.SetMarkerSize(0.5)
    g3.SetMarkerColor(53)
    g3.Draw('P')
    
    g4 = data4.makeGraph('g4', 'Zeit t / s', 'Spannung U / V')
    g4.SetMarkerStyle(8)
    g4.SetMarkerSize(0.5)
    g4.SetMarkerColor(2)
    g4.Draw('P')
    
    
    
    l = TLegend(0.63, 0.51, 0.87, 0.87)
    l.SetTextSize(0.027)
   
   

    l.AddEntry('g1', 'Photodiodensignal,', 'p')
    l.AddEntry('', 'U_{G} = 120 V', '')
    l.AddEntry('g2', 'Photodiodensignal,', 'p')
    l.AddEntry('', 'U_{G} = 122 V', '')
    l.AddEntry('g3', 'Photodiodensignal,', 'p')
    l.AddEntry('', 'U_{G} = 128 V', '')
    l.AddEntry('g4', 'Wechselsignal vom', 'p')
    l.AddEntry('', 'Sinusgenerator mit', '')
    l.AddEntry('', 'Frequenz #omega', '')
    l.SetFillColor(0)
    l.Draw()
  
    
    c.Update()
    c.Print('../img/%s.pdf' % 'pockdurchf', 'pdf')
    
    
    
if __name__ == "__main__":
    main()