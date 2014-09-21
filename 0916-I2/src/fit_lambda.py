#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend
from data import Data
from fitter import Fitter


def fitLambda():
    data = Data()
    data.addPoint(500, 1.000279)
    data.addPoint(540, 1.000278)
    data.addPoint(600, 1.000277)
    data.addPoint(682, 1.000276)

    c = TCanvas('c1', '', 1280, 720)
    g = data.makeGraph('g', 'wavelength #lambda / nm', 'refraction index n')
    g.GetYaxis().SetLabelSize(0.03)
    g.GetYaxis().SetTitleOffset(1.39)
    g.Draw('AP')

    fit = Fitter('f', '[0]+[1]*x')
    fit.setParam(0, 'a', 2)
    fit.setParam(1, 'b', -1)
    fit.fit(g, 450, 700)
    fit.saveData('../calc/fit_lambda.txt', 'w')

    a = fit.params[0]['value']
    sa = fit.params[0]['error']
    b = fit.params[1]['value']
    sb = fit.params[1]['error']

    l = TLegend(0.4, 0.6, 0.87, 0.87)
    l.AddEntry('g', 'refraction index n as a function of wavelength #lambda', 'p')
    l.AddEntry(fit.function, 'fit with n(#lambda)= a+b*#lambda', 'l')
    fit.addParamsToLegend(l)
    l.SetTextSize(0.03)
    l.Draw()

    c.Update()
    c.Print('../img/fit_lambda.pdf', 'pdf')


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    fitLambda()

if __name__ == "__main__":
    main()
