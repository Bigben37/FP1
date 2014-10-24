#!/usr/bin/python2.7
from functions import loadCSVToList
from txtfile import TxtFile


def main():
    phis = [0, 45, 90]
    for phi in phis:
        data = loadCSVToList('../calc/taus_%02d.txt' % phi)
        data.sort(key=lambda x: x[0], reverse=True)
        with TxtFile('../src/taus_%02d.tex' % phi, 'w') as f:
            f.write2DArrayToLatexTable(data, ['$T$ / ${}^{\\circ}$C', '$\\tau$ / ns', '$s_{\\tau} / ns$',
                                              '$\\varphi$ / ${}^{\\circ}$', '$s_{\\varphi}$ / ${}^{\\circ}$'],
                                       ['%d', '%.1f', '%.1f', '%.3f', '%.3f'], 'Fitergebnisse f\"ur $\\varphi=%d$' % phi,
                                       'tab:phi:%0d' % phi)

if __name__ == '__main__':
    main()
