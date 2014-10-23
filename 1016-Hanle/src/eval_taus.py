#!/usr/bin/python2.7
from functions import setupROOT
from hanle import TauData
from ROOT import TCanvas, TLegend
from fitter import Fitter
from txtfile import TxtFile


def main():
    taus = [0, 45, 90]
    for tau in taus:
        data = TauData.fromPath('../calc/taus_%02d.txt' % tau)
        c = TCanvas('taus_%d' % tau, '', 1280, 720)
        g = data.makeGraph('g_%s' % tau, 'Druck p', '#tau / ns')
        g.Draw('AP')
        
        c.Update()
        c.Print('../img/taus_%02d.pdf' % tau, 'pdf')


if __name__ == '__main__':
    setupROOT()
    main()