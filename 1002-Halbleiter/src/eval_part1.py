#!/usr/bin/python2.7
from functions import setupROOT
from ROOT import TCanvas, TLegend
from halbleiter import P1SemiCon
import numpy as np

def evalErrors(elem):
    errorTransPyro = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxTrans.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CPYRO)).getY())
    errorTransSample = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxTrans.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)).getY())
    errorAbsPyro = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxAbs.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CPYRO)).getY())
    errorAbsSample = np.std(P1SemiCon.fromPath('../data/part1/%s_Fehler_MaxAbs.txt' % elem, (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)).getY())
    return max(errorAbsPyro, errorTransPyro), max(errorAbsSample, errorTransSample)

def calcRealIntensity(elem, channel, error):
    data = P1SemiCon.fromPath('../data/part1/%s_Messung.txt' % elem, (P1SemiCon.CENERGY, channel))
    data.setYErrorAbs(error)
    underground = P1SemiCon.fromPath('../data/part1/%s_Untergrund.txt' % elem, (P1SemiCon.CENERGY, channel))
    data.setYErrorAbs(error)
    lamp = P1SemiCon.fromPath('../data/part1/%s_Lampe.txt' % elem, (P1SemiCon.CENERGY, channel))
    lamp.setYErrorAbs(error)
    
    data.subtractUnderground(underground)


def plotMultiChannelSpectrum(elem, mode, multichannels, rangeX, rangeY=(0, 5)):
    label = '%s_%s' % (elem, mode)
    
    c = TCanvas('c_spectrum_%s' % label, '', 1280, 720)
    graphs = []
    for channels in multichannels:
        data = P1SemiCon.fromPath('../data/part1/%s.txt' % label, channels)
        g = data.makeGraph('g_spectrum_%s' % label, P1SemiCon.LABELS[channels[0]], P1SemiCon.LABELS[channels[1]])
        g.SetMarkerStyle(1)
        g.SetMinimum(rangeY[0])
        g.SetMaximum(rangeY[1])
        g.GetXaxis().SetRangeUser(rangeX[0], rangeX[1])
        graphs.append(g)
    
    first = True
    for i, g in enumerate(graphs):
        if first:
            g.Draw('AP')
            first = False
        else:
            g.SetMarkerColor(1 + i)
            g.Draw('P')
    c.Update()
    c.Print('../img/part1/%s_spectrum.pdf' % label, 'pdf')
    

def evalPart1():
    elems = ['Si', 'Ge']
    for elem in elems:
        errors = evalErrors(elem)
        pyro = calcRealIntensity(elem, P1SemiCon.CPYRO, errors[0])
        #plotMultiChannelSpectrum('Si', 'Messung', [(P1SemiCon.CANGLE, P1SemiCon.CPYRO), (P1SemiCon.CANGLE, P1SemiCon.CSAMPLE)], (-5, 80))

def main():
    setupROOT()
    #TODO get errors
    evalPart1()


if __name__ == "__main__":
    main()
