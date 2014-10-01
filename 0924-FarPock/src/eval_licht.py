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
    
    data1 = PockData.fromPath('../data/%s.tab' % 'pock_licht_01', 1)
    data2 = PockData.fromPath('../data/%s.tab' % 'pock_licht_02', 1)
    data3 = PockData.fromPath('../data/%s.tab' % 'pock_licht_03', 1)
    data4 = PockData.fromPath('../data/%s.tab' % 'pock_licht_04', 1)
    
    L0 = [0]*data1.getLength()
    Ly1 = [0]*data1.getLength()
    Ly2 = [0.03]*data1.getLength()
    Ly3 = [0.08]*data1.getLength()
    Ly4 = [0.17]*data1.getLength()
    
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
    g1.SetMarkerColor(1)
    g1.GetXaxis().SetRangeUser(0, 0.1)
    g1.SetMinimum(-0.02)
    g1.SetMaximum(0.25)
    g1.Draw('AP')
    
    g2 = data2.makeGraph('g2', 'Zeit t / s', 'Spannung U / V')
    g2.SetMarkerStyle(8)
    g2.SetMarkerSize(0.5)
    g2.SetMarkerColor(100)
    g2.Draw('P')
    
    g3 = data3.makeGraph('g3', 'Zeit t / s', 'Spannung U / V')
    g3.SetMarkerStyle(8)
    g3.SetMarkerSize(0.5)
    g3.SetMarkerColor(95)
    g3.Draw('P')
    
    g4 = data4.makeGraph('g4', 'Zeit t / s', 'Spannung U / V')
    g4.SetMarkerStyle(8)
    g4.SetMarkerSize(0.5)
    g4.SetMarkerColor(89)
    g4.Draw('P')
    
    
    
    l = TLegend(0.63, 0.51, 0.87, 0.87)
    l.SetTextSize(0.027)
   
   

    l.AddEntry('g4', 'Licht an,', 'p')
    l.AddEntry('', 'ohne Abschirmung', '')
    l.AddEntry('g3', 'Licht an,', 'p')
    l.AddEntry('', 'mit Papier als Abschirmung', '')
    l.AddEntry('g2', 'Licht an,', 'p')
    l.AddEntry('', 'mit Tuch als Abschirmung', '')
    l.AddEntry('g1', 'Licht aus,', 'p')
    l.AddEntry('', 'mit Tuch als Abschirmung', '')
    l.SetFillColor(0)
    l.Draw()
  
    
    c.Update()
    c.Print('../img/%s.pdf' % 'licht', 'pdf')
    
    
    
if __name__ == "__main__":
    main()