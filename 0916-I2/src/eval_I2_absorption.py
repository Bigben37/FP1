#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend, TGaxis
import os
import numpy as np
from I2 import I2Data
from txtfile import TxtFile
from fitter import Fitter

def makeBirgeSponer(data, start):
    """creates Birge-Sponer-plot with given data set
    
    Arguments:
    data  -- I2Data with data to process
    start -- number of first energy level
    """
    plot = I2Data()
    length = data.getLength()
    for i in range(1, length)[::-1]:  # reverse
        l1 = data.points[i][0]
        l2 = data.points[i-1][0]
        plot.addPoint(start + length - (i+1) + 0.5, (1./l2 - 1./l1)*1e7 , 0, I2Data.ERRORBIN*np.sqrt(1./(l1**4) + 1./(l2**4))*1e7)
    return plot

def avgerrors(values, errors):
    """calculates weighted average with error
    
    Arguments:
    values -- values
    errors -- errors
    """
    var = 1. / sum(map(lambda e: 1./(e**2), errors))
    avg = sum(map(lambda v, e: v/(e**2), values, errors)) * var
    return avg, np.sqrt(var)

def getExcitedStateOszillationConstants():
    
    # plot spectrum
    
    data = I2Data.fromPath('../data/04_I2_ngg10_10ms.txt')   
    progression = dict()
    for i in range(1, 3+1):
        progression[i] = I2Data.fromPath('../data/prog%d.txt' % i)

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('spectrum', 'wavelength #lambda / nm', 'intensity')
    g.SetMarkerStyle(1)
    g.GetXaxis().SetRangeUser(505, 620)
    g.SetMinimum(18000)
    g.SetMaximum(49000)
    myY = TGaxis()
    myY.ImportAxisAttributes(g.GetYaxis())
    myY.SetMaxDigits(3)
    g.Draw('AL')
    
    pg1 = progression[1].makeGraph('prog1')
    pg1.SetMarkerColor(2)
    pg1.Draw('P')
    pg2 = progression[2].makeGraph('prog2')
    pg2.SetMarkerColor(3)
    pg2.Draw('P')
    pg3 = progression[3].makeGraph('prog3')
    pg3.SetMarkerColor(4)
    pg3.Draw('P')
    
    l = TLegend(0.6, 0.15, 0.85, 0.4)
    l.AddEntry('spectrum', 'measurement', 'l')
    l.AddEntry('prog1', 'first progression (#nu\'\' = 1)', 'p')
    l.AddEntry('prog2', 'second progression (#nu\'\' = 2)', 'p')
    l.AddEntry('prog3', 'third progression (#nu\'\' = 3)', 'p')
    l.Draw()
    
    c.Update()
    c.Print('../img/I2_absorption.pdf', 'pdf')
    
    # calculations
    
    start = [18, 7, 9]
    prog1ord = {'a':[], 'sa':[], 'b':[], 'sb':[]}
    for i, prog in progression.iteritems():
        
        # Calculate vacuum wavelength and create Birge-Sponer plot
        
        prog.correctValues()
        c = TCanvas('c%d' % i, '', 1280, 720)
        g = makeBirgeSponer(prog, start[i - 1]).makeGraph('prog%d_bs' % i, '#nu\' + 1/2', '#Delta G (#nu\' + 1/2) / (cm^{-1})')
        g.Draw('AP')
        
        # fit 2nd-order
        
        fit2ord = Fitter('prog%d_2ord' % i, '[0]-[1]*(2*x+2)+[2]*(3*x^2+6*x+13/4)')
        fit2ord.setParam(0, 'a', 120)
        fit2ord.setParam(1, 'b', 1)
        fit2ord.setParam(2, 'c', 0)
        fit2ord.fit(g, 4, 50)
        fit2ord.saveData('../calc/prog%d_fit2ord.txt' % i, 'w')      
        l2 = TLegend(0.6, 0.7, 0.95, 0.95)
        l2.AddEntry(0, 'Fit 2nd. order', '')
        l2.AddEntry(fit2ord.function, 'y = a - b*(2*x+2) + c*(3*x^2+6*x+13/4)', 'l')
        fit2ord.addParamsToLegend(l2)
        l2.SetTextSize(0.03)
        l2.Draw()
        
        #fit 1st-order
        
        fit1ord = Fitter('prog%d_1ord' % i, '[0]-[1]*(2*x+2)')
        fit1ord.setParam(0, 'a', 120)
        fit1ord.setParam(1, 'b', 1)
        fit1ord.fit(g, 4, 50, '+')
        g.GetFunction('prog%d_1ord' % i).SetLineColor(4)
        fit1ord.saveData('../calc/prog%d_fit1ord.txt' % i, 'w')
        prog1ord['a'].append(fit1ord.params[0]['value'])
        prog1ord['sa'].append(fit1ord.params[0]['error'])
        prog1ord['b'].append(fit1ord.params[1]['value'])
        prog1ord['sb'].append(fit1ord.params[1]['error'])
        l1 = TLegend(0.125, 0.15, 0.5, 0.4)
        l1.AddEntry(0, 'Fit 1st. order', '')
        l1.AddEntry(g.GetFunction('prog%d_1ord' % i), 'y = a - b*(2*x+2)', 'l')
        fit1ord.addParamsToLegend(l1)
        l1.SetTextSize(0.03)
        l1.Draw()
        
        c.Update()
        c.Print('../img/prog%d_birgesponer.pdf' % i, 'pdf')
        
    # calculate weighted average for fit 1st- order
        
    with TxtFile.fromRelPath('../calc/ExcitedStateOszillationConstants.txt', 'w') as f:
        f.writeline('\t', *map(lambda x: str(x), avgerrors(prog1ord['a'], prog1ord['sa']))) 
        f.writeline('\t', *map(lambda x: str(x), avgerrors(prog1ord['b'], prog1ord['sb'])))
    
def intersect(listA, listB):
    return list(set(listA) & set(listB))
        
def getAverageDeltaEnergy(lowprog, highprog):
    # load data
    lp = I2Data.fromPath(lowprog)
    lp.correctValues(False)
    lp.invertY()
    lp.multiplyY(1e7)  # from 1/nm to 1/cm
    hp = I2Data.fromPath(highprog)
    hp.correctValues(False)
    hp.invertY()
    hp.multiplyY(1e7)  # from 1/nm to 1/cm
    
    # get same values for same nus
    sameNus = intersect(lp.getX(), hp.getX())
    deltas = []
    deltas_errors = []
    for nu in sameNus:
        hv = hp.getByX(nu)  # high value
        hy = hv[1]          # high y
        hye = hv[3]         # high error
        lv = lp.getByX(nu)  # low value
        ly = lv[1]          # low y
        lye = lv[3]         # low error
        deltas.append(hy - ly)
        deltas_errors.append(np.sqrt(hye**2 + lye**2))
    return avgerrors(deltas, deltas_errors)

def getGroundStateOszillationConstants():
    dg12, dg12e = getAverageDeltaEnergy('../data/prog2nl.txt', '../data/prog1nl.txt')
    dg32, dg32e = getAverageDeltaEnergy('../data/prog3nl.txt', '../data/prog2nl.txt')
    we, wee = 2*dg12 - dg32, np.sqrt(4*(dg12e**2) + dg32e**2)  # w_e, s_w_e
    wexe, wexee = 0.5 * (dg12 - dg32), 0.5*np.sqrt(dg12e**2 + dg32e**2)  # w_e x_e, s_(w_e x_e)
    with TxtFile('../calc/GroundStateOszillationConstants.txt', 'w') as f:
        f.writeline('\t', str(we), str(wee))
        f.writeline('\t', str(wexe), str(wexee))
        
def loadOszillationConstants(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        consts = []
        with open(p, 'r') as f:
            for line in f:
                consts.append(list(map(lambda x: float(x), line.strip().split('\t'))))  # remove \n, split by \t, convert to float
        return consts

def calcualteDissEnergyFromMorse(w_e, w_ex_e):
    we = w_e[0]
    wee = w_e[1]
    wexe = w_ex_e[0]
    wexee = w_ex_e[1]
    val =  we**2 / (4*wexe)
    err = val * np.sqrt(4*(wee / we)**2 + (wexee / wexe)**2)
    return str(val), str(err)
        
def calculateDissEnergiesFromMorse():
    with TxtFile('../calc/ExcitedStateDissEnergyFromMorse.txt', 'w') as f:
        f.writeline(' \t', *calcualteDissEnergyFromMorse(*loadOszillationConstants('../calc/ExcitedStateOszillationConstants.txt')))
        
    with TxtFile('../calc/GroundStateDissEnergyFromMorse.txt', 'w') as f:
        f.writeline(' \t', *calcualteDissEnergyFromMorse(*loadOszillationConstants('../calc/GroundStateOszillationConstants.txt')))
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    #getExcitedStateOszillationConstants()
    #getGroundStateOszillationConstants()
    calculateDissEnergiesFromMorse()

if __name__ == "__main__":
    main()