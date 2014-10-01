#!/usr/bin/python2.7
from functions import loadCSVToList
import numpy as np
from txtfile import TxtFile

def main():
    data = loadCSVToList('../data/fara_2epsilon.txt')
    inner = np.average(data[0])
    outer = np.average(data[1])
    dif  = 180 + outer - inner
    error = 2.0 * np.sqrt(2) / np.sqrt(len(data[0]))
    
    with TxtFile('../calc/fara_2epsilon.txt', 'w') as f:
        f.writeline('\t', str(dif), str(error))

if __name__ == "__main__":
    main()