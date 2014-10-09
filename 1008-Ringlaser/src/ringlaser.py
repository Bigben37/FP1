#!/usr/bin/python2.7
from data import DataErrors  # make sure to add ../lib to your project path or copy file from there
from functions import loadCSVToList  # make sure to add ../lib to your project path or copy file from there
from numpy import pi

st_mult = 5

class X0Data(DataErrors):  # for variable x0
    SX = 0.05
    ST = 0.2

    def loadData(self):
        datalist = loadCSVToList(self.path)
        for row in datalist:
            x, N, t, st = row
            t /= 1000  # in ms
            st /= 1000  # in ms
            st *= st_mult
            nu = N / t
            snu = abs(N * st / t ** 2)  # sy = y * (st / t)
            self.addPoint(nu, x, snu, X0Data.SX)


class TData(DataErrors):  # for variable T
    SX = 0.05
    ST = 0.2
    
    def loadData(self):
        datalist = loadCSVToList(self.path)
        for row in datalist:
            T, N, t, st = row
            t /= 1000  # in ms
            st /= 1000  # in ms
            st *= st_mult
            nu = N / t
            snu = abs(N * st / t ** 2)  # sy = y * (st / t)
            w = 2 * pi / T
            sw = 2 * pi * TData.ST / T ** 2# w * TData.ST / T
            self.addPoint(w, nu, sw, snu)