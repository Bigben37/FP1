#!/usr/bin/python2.7
# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from functions import loadCSVToList
from txtfile import TxtFile
# ========================================================================


def makeBfields_fit():
    bfields = loadCSVToList('../calc/bfields_leiterschleife_fit.txt')
    bfields = [(B * 1e9, sB * 1e9) for B, sB in bfields]
    res = [100, 510, 1000, 5100, 10000]
    data = zip(res, *zip(*bfields))
    with TxtFile('../src/bfields_fit.tex', 'w') as f:
        f.write2DArrayToLatexTable(data, ['$R$ / \\textOmega', '$B_z$ / nT', '$s_{B_z}$ / nT'],
                                   ['%d', '%.5f', '%.5f'],
                                   'Gemessene Magnetfeldst\"arke $B_z$ in Abh\"angigkeit des Widerstandes $R$ der Leiterschleife.',
                                   'tab:B:fit')


def makeBfields_theo():
    bfields = loadCSVToList('../calc/bfields_leiterschleife_theo.txt')
    bfields = [(B * 1e9, sB * 1e9) for B, sB in bfields]
    resistors = loadCSVToList('../data/resistors.txt')
    I = [u / r * 1000 for r, u in resistors]
    sI = [0.01 / r * 1000 for r, u in resistors]
    data = zip(I, sI, *zip(*bfields))
    with TxtFile('../src/bfields_theo.tex', 'w') as f:
        f.write2DArrayToLatexTable(data, ['$I$ / mA', '$s_I$ / mA', '$B_z$ / nT', '$s_{B_z}$ / nT'],
                                   ['%.4f', '%.4f', '%.3f', '%.3f'],
                                   'Theoretische Magnetfeldst\"arke $B_z$ in Abh\"angigkeit des Stroms $I$, der durch die Leiterschleife flie\"st.',
                                   'tab:B:theo')


def main():
    makeBfields_fit()
    makeBfields_theo()

if __name__ == '__main__':
    main()
