#!/usr/bin/python2.7

from functions import loadCSVToList
from txtfile import TxtFile

import numpy as np


def main():
    R = (3.2 + 4.4) / 4 / 1000  # from mm to m
    sR = 0.5 / (2 * np.sqrt(2)) / 1000  # from mm to m

    z = (29 - 26.5) / 100  # from cm to m
    sz = 0.2 * np.sqrt(2) / 100  # from cm m

    mu = 4e-7 * np.pi  # V*s/(A*m)
    sU = 0.01  # in V, 1 digit

    data = loadCSVToList('../data/resistors.txt')
    bfields = []
    for res, U in data:  # res in ohm, U in volts
        B = (mu * U * (R ** 2)) / (2 * res) / ((R ** 2 + z ** 2) ** (3. / 2))
        sB = (R * mu / (2 * res * ((R ** 2 + z ** 2) ** (5. / 2))) *
              np.sqrt(R ** 6 * sU ** 2 + 4 * sR ** 2 * U ** 2 * z ** 4 + R ** 2 * z ** 2 *
                      ((-4 * sR ** 2 + 9 * sz ** 2) * U ** 2 + sU ** 2 * z ** 2) + R ** 4 *
                      (sR ** 2 * U ** 2 + 2 * sU ** 2 * z ** 2)))
        bfields.append((B, sB))

    with TxtFile('../calc/bfields_leiterschleife_theo.txt', 'w') as f:
        for B in bfields:
            f.writeline('\t', *map(str, B))

if __name__ == '__main__':
    main()
