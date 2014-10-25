#!/usr/bin/python2.7
"""Create LaTeX tables from multiple csv-files"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"
# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from functions import loadCSVToList
from txtfile import TxtFile
# ========================================================================


def makeTauTables():  # table with fitted taus and angles for each position
    phis = [0, 45, 90]
    for phi in phis:
        data = loadCSVToList('../calc/taus_%02d.txt' % phi)
        data.sort(key=lambda x: x[0], reverse=True)
        with TxtFile('../src/taus_%02d.tex' % phi, 'w') as f:
            f.write2DArrayToLatexTable(data, ['$T$ / ${}^{\\circ}$C', '$\\tau$ / ns', '$s_{\\tau}$ / ns',
                                              '$\\Phi$ / ${}^{\\circ}$', '$s_{\\Phi}$ / ${}^{\\circ}$'],
                                       ['%d', '%.1f', '%.1f', '%.3f', '%.3f'], 'Fitergebnisse f\"ur $\\Phi=%d^\\circ$.' % phi,
                                       'tab:phi:%0d' % phi)


def makeTempTable():  # table with calculated pressures
    data = loadCSVToList('../calc/temp_pressure.txt')
    data.sort(key=lambda x: x[0], reverse=True)
    with TxtFile('../src/temp_pressure.tex', 'w') as f:
        f.write2DArrayToLatexTable(data, ['$T$ / ${}^{\\circ}$C', '$p$ / mPa', '$s_p$ / mPa'],
                                   ['%d', '%.0f', '%.0f'], 'Dampfdruck von Quecksilber bei verschiedenen Temperaturen.',
                                   'tab:pressure')


def makePhiTable():  # table with fitted angles and position angles
    data = loadCSVToList('../calc/avgphis.txt')
    data.sort(key=lambda x: x[0])
    with TxtFile('../src/avgphis.tex', 'w') as f:
        f.write2DArrayToLatexTable(data, ['$\\Phi$ / ${}^{\\circ}$', '$\\Phi_\\text{fit}$ / ${}^{\\circ}$',
                                          '$s_{\\Phi_\\text{fit}}$ / ${}^{\\circ}$'],
                                   ['%d', '%.2f', '%.2f'],
                                   'Theoretischer und gefitteter Winkel der drei Einstellungen am Aufbau.',
                                   'tab:avgphis')


def main():
    makeTauTables()
    makeTempTable()
    makePhiTable()

if __name__ == '__main__':
    main()
