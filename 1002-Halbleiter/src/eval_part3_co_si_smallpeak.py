#!/usr/bin/python2.7
from functions import loadCSVToList, setupROOT
from data import DataErrors
from fitter import Fitter
from txtfile import TxtFile
from ROOT import TCanvas, TLegend

def main():
    x, y, sy = zip(*loadCSVToList('../calc/part3/Co-Si_mergedbins.txt'))
    data = DataErrors.fromLists(x, y, [0]*len(x), sy)
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'Kanal k', 'Counts N')
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.5)
    g.SetLineColor(15)
    g.SetLineWidth(0)
    g.Draw('AP')
    
    fit = Fitter('f', '1/(sqrt(2*pi*[2]^2))*gaus(0)')
    fit.setParam(0, 'A', 50)
    fit.setParam(1, 'x_{c}', 690)
    fit.setParam(2, 's', 20)
    fit.fit(g, 672, 712)
    fit.saveData('../calc/part3/fit_Co-Si_01_mergedbins.txt', 'w')
    with TxtFile('../calc/part3/fit_Co-Si_01_mergedbins_raw.txt', 'w') as f:
        for key, param in fit.params.iteritems():
            f.writeline('\t', *map(str, [param['value'], param['error']]))
    
    l = TLegend(0.7, 0.5, 0.95, 0.85)
    l.SetTextSize(0.0225)
    l.AddEntry(g, 'Gemittelte Messwerte', 'p')
    l.AddEntry(fit.function, 'Fit mit', 'l')
    l.AddEntry(0, 'N(k) = #frac{A}{#sqrt{2#pi*#sigma^{2}}} exp(- #frac{1}{2} (#frac{x-x_{c}}{#sigma})^{2})', '')
    l.AddEntry(0, '', '')
    fit.addParamsToLegend(l, chisquareformat='%.2f')
    l.Draw()
    
    c.Update()
    c.Print('../img/part3/Co-Si_01_mergedbins.pdf', 'pdf')


if __name__ == "__main__":
    setupROOT()
    main()