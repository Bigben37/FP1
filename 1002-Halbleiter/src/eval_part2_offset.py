#!/usr/bin/python2.7
from txtfile import TxtFile
import numpy as np

def main():
    offsets = [1.32, 1.18]
    error = 0.2
    with TxtFile('../calc/part2/offset.txt', 'w') as f:
        f.writeline('\t', str(np.average(offsets)), str(error / np.sqrt(len(offsets))))

if __name__ == "__main__":
    main()