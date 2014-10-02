#!/usr/bin/python2.7

from functions import loadCSVToList, avgerrors
from farpock import calcr41
from txtfile import TxtFile
import numpy as np


def eval(freq):
    # load data
    data = loadCSVToList('../data/pock_gleich_%dhz.txt' % freq)
    sv = 1  # error on single meassurement

    # calculate r41
    diffs = map(lambda x: (x[0] + x[1], np.sqrt(2) * sv), data)
    avg = avgerrors(*zip(*diffs))
    return calcr41(*avg)


def main():
    freqs = [1e3, 1e4]
    with TxtFile('../calc/pock_dc.txt', 'w') as f:
        r41s = []
        for freq in freqs:
            r41 = eval(freq)
            r41s.append(r41)
            f.writeline('\t', str(freq), *map(str, r41))
        f.writeline('average:')
        f.writeline('\t', *map(str, avgerrors(*zip(*r41s))))

if __name__ == "__main__":
    main()
