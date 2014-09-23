#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TLegend, TGaxis, TF1
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
        l2 = data.points[i - 1][0]
        plot.addPoint(start + length - (i + 1) + 0.5, (1. / l2 - 1. / l1) * 1e7, 0, I2Data.ERRORBIN * np.sqrt(1. / (l1 ** 4) + 1. / (l2 ** 4)) * 1e7)
    return plot


def avgerrors(values, errors):
    """calculates weighted average with error

    Arguments:
    values -- values
    errors -- errors
    """
    var = 1. / sum(map(lambda e: 1. / (e ** 2), errors))
    avg = sum(map(lambda v, e: v / (e ** 2), values, errors)) * var
    return avg, np.sqrt(var)


def getExcitedStateOscillationConstants():

    # plot spectrum

    data = I2Data.fromPath('../data/04_I2_ngg10_10ms.txt')
    progression = dict()
    for i in range(1, 3 + 1):
        progression[i] = I2Data.fromPath('../data/prog%d.txt' % i)

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('spectrum', 'wavelength #lambda / nm', 'intensity / a.u.')
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
    prog1ord = {'a': [], 'ae': [], 'b': [], 'be': []}
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

        # fit 1st-order

        fit1ord = Fitter('prog%d_1ord' % i, '[0]-[1]*(2*x+2)')
        fit1ord.setParam(0, 'a', 120)
        fit1ord.setParam(1, 'b', 1)
        fit1ord.fit(g, 4, 50, '+')
        g.GetFunction('prog%d_1ord' % i).SetLineColor(4)
        fit1ord.saveData('../calc/prog%d_fit1ord.txt' % i, 'w')
        prog1ord['a'].append(fit1ord.params[0]['value'])
        prog1ord['ae'].append(fit1ord.params[0]['error'])
        prog1ord['b'].append(fit1ord.params[1]['value'])
        prog1ord['be'].append(fit1ord.params[1]['error'])
        l1 = TLegend(0.125, 0.15, 0.5, 0.4)
        l1.AddEntry(0, 'Fit 1st. order', '')
        l1.AddEntry(g.GetFunction('prog%d_1ord' % i), 'y = a - b*(2*x+2)', 'l')
        fit1ord.addParamsToLegend(l1)
        l1.SetTextSize(0.03)
        l1.Draw()

        c.Update()
        c.Print('../img/prog%d_birgesponer.pdf' % i, 'pdf')

    # save vibrational constants to latex file
    nus = [0, 1, 2]
    f = TxtFile('../src/ExcitedStateOscillationConstants.tex', 'w')
    f.write2DArrayToLatexTable(zip(nus, prog1ord['a'], prog1ord['ae'], prog1ord['b'], prog1ord['be']), 
                               ['$\\nu\'\'$', '$\omega_e\' / \\text{cm}^{-1}$', '$s_{\omega_e\'} / \\text{cm}^{-1}$', 
                                '$\omega_e\' x_e\' / \\text{cm}^{-1}$', '$s_{\omega_e\' x_e\'} / \\text{cm}^{-1}$'], 
                               ['%0.f', '%3.1f', '%.1f', '%.3f', '%.3f'], 
                               'Oscillation constants for first order fit of Birge-Sponer plots', 'tab:prog1ord')
    f.close()


    # calculate weighted average for fit 1st- order

    with TxtFile.fromRelPath('../calc/ExcitedStateOscillationConstants.txt', 'w') as f:
        f.writeline('\t', *map(lambda x: str(x), avgerrors(prog1ord['a'], prog1ord['ae'])))
        f.writeline('\t', *map(lambda x: str(x), avgerrors(prog1ord['b'], prog1ord['be'])))


def intersect(listA, listB):
    return list(set(listA) & set(listB))


def getAverageDeltaEnergy(lowprog, highprog):
    # load data
    lp = I2Data.fromPath(lowprog)
    lp.correctValues(useX=False)
    lp.invertY()
    lp.multiplyY(1e7)  # from 1/nm to 1/cm
    hp = I2Data.fromPath(highprog)
    hp.correctValues(useX=False)
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
        deltas_errors.append(np.sqrt(hye ** 2 + lye ** 2))
    return avgerrors(deltas, deltas_errors)


def getGroundStateOscillationConstants():
    dg12, dg12e = getAverageDeltaEnergy('../data/prog2nl.txt', '../data/prog1nl.txt')
    dg32, dg32e = getAverageDeltaEnergy('../data/prog3nl.txt', '../data/prog2nl.txt')
    we, wee = 2 * dg12 - dg32, np.sqrt(4 * (dg12e ** 2) + dg32e ** 2)  # w_e, s_w_e
    wexe, wexee = 0.5 * (dg12 - dg32), 0.5 * np.sqrt(dg12e ** 2 + dg32e ** 2)  # w_e x_e, s_(w_e x_e)
    with TxtFile('../calc/GroundStateOscillationConstants.txt', 'w') as f:
        f.writeline('\t', str(we), str(wee))
        f.writeline('\t', str(wexe), str(wexee))


def loadCSVToList(path, delimiter='\t'):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        consts = []
        with open(p, 'r') as f:
            for line in f:
                consts.append(list(map(lambda x: float(x), line.strip().split(delimiter))))  # remove \n, split by delimiter, convert to float
        return consts


def calcualteDissEnergyFromMorse(w_e, w_ex_e):
    we = w_e[0]
    wee = w_e[1]
    wexe = w_ex_e[0]
    wexee = w_ex_e[1]
    val = we ** 2 / (4 * wexe)
    err = val * np.sqrt(4 * (wee / we) ** 2 + (wexee / wexe) ** 2)
    return str(val), str(err)


def calculateDissEnergiesFromMorse():
    with TxtFile('../calc/ExcitedStateDissEnergyFromMorse.txt', 'w') as f:
        f.writeline(' \t', *calcualteDissEnergyFromMorse(*loadCSVToList('../calc/ExcitedStateOscillationConstants.txt')))

    with TxtFile('../calc/GroundStateDissEnergyFromMorse.txt', 'w') as f:
        f.writeline(' \t', *calcualteDissEnergyFromMorse(*loadCSVToList('../calc/GroundStateOscillationConstants.txt')))


def getParamsFromFittingInfo(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        params = dict()
        with open(p, 'r') as f:
            for line in f:
                l = line.strip().split('\t')
                if len(l) == 5:
                    params[l[1]] = {'value': float(l[2]), 'error': float(l[2])}
        return params


def getCorrelationFrom2DMatrix(path):
    if path:
        d = os.path.dirname(os.path.abspath(__file__))
        p = os.path.abspath(os.path.join(d, path))
        inCorrSection = False
        with open(p, 'r') as f:
            for line in f:
                if inCorrSection:
                    l = line.strip().split('\t')
                    if len(l) == 2:
                        return float(l[1])
                if 'correlation matrix' in line:
                    inCorrSection = True


def calculateExcitationEnergy():
    prog = 1
    n = 18
    m = 0

    # get G'(nu = n)
    absEnergy = I2Data.fromPath('../data/prog%dnl.txt' % prog)
    absEnergy.correctValues(useX=False)
    absEnergy.invertY()
    absEnergy.multiplyY(1e7)
    G = absEnergy.getByX(n)[1]
    Ge = absEnergy.getByX(n)[3]

    # get DeltaG from model
    params = getParamsFromFittingInfo('../calc/prog%d_fit1ord.txt' % prog)
    rho = getCorrelationFrom2DMatrix('../calc/prog%d_fit1ord.txt' % prog)
    a = params['a']['value']
    ae = params['a']['error']
    b = params['b']['value']
    be = params['b']['error']
    dg = a - b * (2 * m + 2)
    dge = np.sqrt(ae ** 2 - 4 * (1 + m) * rho * ae * be + 4 * ((1 + m) * be) ** 2)
    dgn = a - b * (2 * n + 2)
    dgne = np.sqrt(ae ** 2 - 4 * (1 + n) * rho * ae * be + 4 * ((1 + n) * be) ** 2)

    # calculate excitation energy
    E = G - n / 2 * (dg + dgn)
    Ee = np.sqrt(Ge ** 2 + (dge * n) ** 2 / 4 + (dgne * n) ** 2 / 4)

    # output to file
    with TxtFile('../calc/ExcitationEnergy.txt', 'w') as f:
        f.writeline('\t', str(E), str(Ee))


def calculateGroundStateDissEnergyFromDiff():
    # get energies
    excitedStateDissEnergy = loadCSVToList('../calc/ExcitedStateDissEnergyFromMorse.txt')[0]
    excitationEnergy = loadCSVToList('../calc/ExcitationEnergy.txt')[0]
    deltaP = 7603

    # calculate ground state dissoziation energy
    E = excitationEnergy[0] + excitedStateDissEnergy[0] - deltaP
    Ee = np.sqrt(excitationEnergy[1] ** 2 + excitedStateDissEnergy[1] ** 2)

    # write to file
    with TxtFile('../calc/GroundStateDissEnergyFromDiff.txt', 'w') as f:
        f.writeline('\t', str(E), str(Ee))


def plotMorsePotential():
    # constants
    h = 6.63e-34
    c = 3e8
    M = 0.5 * 126.9 * 1.66e-27
    Be = 2.9
    pi = np.pi

    # load variables
    we, wee = loadCSVToList('../calc/ExcitedStateOscillationConstants.txt')[0]
    De, Dee = loadCSVToList('../calc/ExcitedStateDissEnergyFromMorse.txt')[0]

    # calculate values
    re = np.sqrt(h / (8 * pi ** 2 * c * M * Be)) * 1e10
    a = we * 100 * np.sqrt(2 * pi ** 2 * c * M / (h * De * 100)) * 1e-10
    ae = a * np.sqrt((wee/we)**2 + (Dee/(2*De))**2)
    
    with TxtFile('../calc/morse.txt', 'w') as f:
        f.writeline('\t', 'D_e', str(De), str(Dee))
        f.writeline('\t', 'a', str(a), str(ae))
        f.writeline('\t', 'r_e', str(re))

    c = TCanvas('cmorse', '', 1280, 720)
    f = TF1('morse', '[0]*(1-exp(-1*[1]*(x-[2])))^2', 2, 7)
    f.SetParameter(0, De)
    f.SetParameter(1, a)
    f.SetParameter(2, re)
    f.SetMaximum(10000)
    f.SetTitle("")
    f.GetXaxis().SetTitle('Internuclear Seperation r / #AA')
    f.GetXaxis().CenterTitle()
    f.GetYaxis().SetTitle('Energy E/hc / (cm^{-1})')
    f.GetYaxis().CenterTitle()
    f.Draw()
    c.Update()
    c.Print('../img/morse.pdf', 'pdf')


def makeProgTables():
    name = 'prog%dnl.txt'
    for i in range(1, 3 + 1):
        prog = I2Data.fromPath('../data/' + name % i)
        x = prog.getX()
        y = prog.getY()
        prog.correctValues(False)
        yc = prog.getY()
        yce = prog.getEY()
        f = TxtFile('../src/prog%d.tex' % i, 'w')
        f.write2DArrayToLatexTable(zip(x, y, yc, yce),
                                   ['$\\nu\'$', r'$\lambda_{\text{exp}}$ / nm', r'$\lambda_{\text{cor}}$ / nm', r'$s_{\lambda_{\text{cor}}}$ / nm'],
                                   ['%0.f', '%3.2f', '%3.2f', '%.8f'],
                                   'Measured position of transmission minima in $I_2$-spectrum and corrected values of progession %d.' % i,
                                   'tab:prog%d' % i)
        f.close()


def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    getExcitedStateOscillationConstants()
    getGroundStateOscillationConstants()
    calculateDissEnergiesFromMorse()
    calculateExcitationEnergy()
    calculateGroundStateDissEnergyFromDiff()
    plotMorsePotential()
    makeProgTables()

if __name__ == "__main__":
    main()
