from farpock import PockData
from fitter import Fitter
from ROOT import gROOT, gStyle, TCanvas, TLegend
from functions import avgerrors
import numpy as np
from txtfile import TxtFile

#eval methoden

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    
    params = []
    fitlist = [False, True, True, True]
    for i in xrange(4):
        param = eval('pock_saege_winkel%d' % i, fitlist[i])
        if fitlist[i]:
            params.append(param)
            

    difflist = []            
    for i in xrange(3):
        difflist.append((params[i][1][0]-params[i][0][0],np.sqrt(params[i][1][1]**2 + params[i][0][1]**2)))
    
    print(difflist)
    print(zip(*difflist))
    av = avgerrors(*zip(*difflist))
    print(av)
    
    with TxtFile('../calc/diff_minmax.txt', 'w') as f:
        for dif in difflist:
            f.writeline('\t', *map(str, dif))
        f.writeline('\t', str(av[0]),str(av[1]),'weighted average')
      
   

def eval(name,f):
    """description
    
    Arguments:
    name -- 
    f --
    """
       
    dataCH1 = PockData.fromPath('../data/%s.tab' % name, 1)
    dataCH2 = PockData.fromPath('../data/%s.tab' % name, 2)
    
    c = TCanvas('c', '', 1280, 720)
    
    g1 = dataCH1.makeGraph('g1', 'Zeit t / s', 'Spannung U / V')
    g1.SetMarkerStyle(8)
    g1.SetMarkerSize(0.5)
    g1.SetMarkerColor(2)
    g1.GetXaxis().SetRangeUser(0.01, 0.04)
    g1.SetMinimum(-3.2)
    g1.SetMaximum(5)
    g1.Draw('AP')
    
    g2 = dataCH2.makeGraph('g2', 'Zeit t / s', 'Spannung U / V')
    g2.SetMarkerStyle(8)
    g2.SetMarkerSize(0.5)
    g2.SetMarkerColor(4)
    g2.Draw('P')
    
    paramlist = []
    
    if f:
        #fit1 = Fitter('f1', '[0]+[1]*x')
        #fit1.function.SetLineWidth(2)
        #fit1.function.SetLineColor(1)
        #fit1.setParam(0, 'a', -5)
        #fit1.setParam(1, 'b', 300)
        #fit1.fit(g1, 0.015, 0.029)
        #fit1.saveData('../calc/fit1.txt', 'w')
        
        fit2 = Fitter('f2', '[0]*(x-[1])**2+[2]')
        fit2.function.SetLineWidth(2)
        fit2.function.SetLineColor(1)
        fit2.setParam(0, 'a', 400000)
        fit2.setParam(1, 's', 0.017)
        fit2.setParam(2, 'c', -2)
        fit2.fit(g2, 0.015, 0.0202, '+')
        #fit2.saveData('../calc/fit2.txt', 'w')
        
        fit3 = Fitter('f2', '[0]*(x-[1])**2+[2]')
        fit3.function.SetLineWidth(2)
        fit3.function.SetLineColor(1)
        fit3.function.SetLineStyle(2)
        fit3.setParam(0, 'a', -200000)
        fit3.setParam(1, 's', 0.023)
        fit3.setParam(2, 'c', 2)
        fit3.fit(g2, 0.0202, 0.0275, '+')
        #fit3.saveData('../calc/fit3.txt', 'w')
    
        l = TLegend(0.635, 0.52, 0.87, 0.87)
        l.AddEntry('g1', 'S#ddot{a}gezahnspannung', 'p')
        #l.AddEntry(fit1.function, 'Fit mit y = a + b*x', 'l')
        #l.AddEntry(0, 'a = %.3f #pm %.3f' % (fit1.params[0]['value'], fit1.params[0]['error']), '')
        #l.AddEntry(0, 'b = %.1f #pm %.1f' % (fit1.params[1]['value'], fit1.params[1]['error']), '')
        l.AddEntry('g2', 'Signal der Photodiode', 'p')
        l.AddEntry(fit2.function, 'Fit mit y = a1 * (x-s1)^2 + b1', 'l')
        l.AddEntry(0, 's1 = %.6f #pm %.6f' % (fit2.params[1]['value'], fit2.params[1]['error']), '')
        l.AddEntry(fit3.function, 'Fit mit y = a2 * (x-s2)^2 + b2', 'l')
        l.AddEntry(0, 's2 = %.6f #pm %.6f' % (fit3.params[1]['value'], fit3.params[1]['error']), '')
        l.SetFillColor(0)
        l.Draw()
        
        paramlist = [(fit2.params[1]['value'], fit2.params[1]['error']),
                     (fit3.params[1]['value'], fit3.params[1]['error'])]
        
    else:
        l = TLegend(0.635, 0.72, 0.85, 0.87)
        l.AddEntry('g1', 'S#ddot{a}gezahnspannung', 'p')
        l.AddEntry('g2', 'Signal der Photodiode', 'p')
        l.SetFillColor(0)
        l.Draw()
    
    c.Update()
    c.Print('../img/%s.pdf' % name, 'pdf')
    
    return paramlist
    
if __name__ == "__main__":
    main()