#!/usr/bin/python2.7
from functions import setupROOT, avgerrors, loadCSVToList  # make sure to add ../lib to your project path or copy file from there
from txtfile import TxtFile  # make sure to add ../lib to your project path or copy file from there


def loadAlpha(path):
    data = loadCSVToList(path)
    return data[-1]


def getCalcAlpha():
    # consts, all lengths in cm
    dndla = -300
    n = 1.457
    la = 6.3282e-5
    return 1 - 1 / n ** 2 - la / n * dndla


def main():
    alpha_fixed_x0 = loadAlpha('../calc/fixed_x0_alpha.txt')
    alpha_fixed_T = loadAlpha('../calc/fixed_T_alpha.txt')
    alphas = [alpha_fixed_T, alpha_fixed_x0]
    with TxtFile('../calc/alpha_calc.txt', 'w') as f:
        f.writeline('\t', *map(str, avgerrors(*zip(*alphas))))
        f.writeline(str(getCalcAlpha()))

if __name__ == '__main__':
    main()
