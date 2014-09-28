#!/usr/bin/python2.7
"""some useful functions which dont fit in any class"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

import os


def loadCSVToList(path, delimiter='\t'):
    """loads data in CSV-file to a list of lists.

    Arguments:
    path      -- relative path to file
    delimiter -- delimiter of file (default='\t')
    """
    if path:
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, path))
        data = []
        with open(p, 'r') as f:
            for line in f:
                data.append(list(map(lambda x: float(x), line.strip().split(delimiter))))  # remove \n, split by delimiter, convert to float
        return data