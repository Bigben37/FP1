#!/usr/bin/python2.7
from functions import setupROOT, loadCSVToList  # make sure to add ../lib to your project path or copy file from there
from kernspin import ERRORS
from data import DataErrors
from ROOT import TCanvas, TLegend
from txtfile import TxtFile
from fitter import Fitter
import numpy as np


def calcGyro(nu, snu, B, sB):
    nu *= 1e6  # MHz -> Hz
    snu *= 1e6  # MHz -> Hz
    B /= 1e3  # mT -> T
    sB /= 1e3  # mT -> T
    gyro = 2 * np.pi * nu / B
    sgyro = gyro * np.sqrt((snu / nu) ** 2 + (sB / B) ** 2)
    return gyro, sgyro


def calcMu(gyro, sgyro):
    hbar = 1.05457173e-34  # m^2 * kg / s
    return map(lambda x: 0.5 * hbar * x, (gyro, sgyro))  # mu, smu


def calcNucGFactor(gyro, sgyro):
    hbar = 1.05457173e-34  # m^2 * kg / s
    mu_n = 5.05078353e-27  # in J / T
    return map(lambda x: x * hbar / mu_n, (gyro, sgyro))  # g, sg


def main():
    snu = ERRORS['nu']  # TODO get error
    sB = ERRORS['B']
    sgyrorel = 0
    files = ['H', 'Glycol', 'Teflon']
    for file in files:
        datalist = loadCSVToList('../data/03-%s.txt' % file)
        if len(datalist) == 1:
            B, nu = datalist[0]
            gyro, sgyro = calcGyro(nu, snu, B, sB)
            if not sgyrorel == 0:
                sgyro = gyro * sgyrorel 
            with TxtFile('../calc/%s.txt' % file, 'w') as f:
                f.writeline('\t', 'gyro', *map(str, (gyro, sgyro)))
                f.writeline('\t', 'mu', *map(str, calcMu(gyro, sgyro)))
                f.writeline('\t', 'gI', *map(str, calcNucGFactor(gyro, sgyro)))
        else:
            x, y = zip(*datalist)
            sx = [0] * len(x)
            sy = [snu] * len(y)
            data = DataErrors.fromLists(x, y, sx, sy)
            data.setXErrorAbs(sB)
            c = TCanvas('c%s' % file, '', 1280, 720)
            g = data.makeGraph('g%s' % file, 'Magnetfeld B / mT', 'Resonanzfrequenz #nu / MHz')
            g.Draw('AP')

            fit = Fitter('fit%s' % file, '[0]*x')
            fit.setParam(0, 'm', 0.002)
            fit.fit(g, datalist[0][0] * 0.95, datalist[-1][0] * 1.05)
            fit.saveData('../calc/fit-%s.txt' % file, 'w')

            l = TLegend(0.15, 0.60, 0.475, 0.85)
            l.SetTextSize(0.03)
            l.AddEntry(g, 'Messdaten', 'p')
            l.AddEntry(fit.function, 'Fit mit #nu(B) = m*B', 'l')
            l.AddEntry(0, '', '')
            fit.addParamsToLegend(l, [('%.5f', '%.5f'), ('%.2f', '%.2f')], chisquareformat='%.2f', advancedchi=True,
                                  units=['MHz / mT', 'MHz'])
            l.Draw()

            gyro = 2 * np.pi * fit.params[0]['value'] * 1e9  # in Hz / T
            sgyro = 2 * np.pi * fit.params[0]['error'] * 1e9  # in Hz / T
            sgyrorel = sgyro / gyro
            with TxtFile('../calc/%s.txt' % file, 'w') as f:
                f.writeline('\t', 'gyro', *map(str, (gyro, sgyro)))
                f.writeline('\t', 'sgyrorel', str(sgyrorel))
                f.writeline('\t', 'mu', *map(str, calcMu(gyro, sgyro)))
                f.writeline('\t', 'gI', *map(str, calcNucGFactor(gyro, sgyro)))

            c.Update()
            c.Print('../img/03-%s.pdf' % file, 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()
