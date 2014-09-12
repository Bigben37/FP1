#!/usr/bin/python2.7
from ROOT import TF1, TVirtualFitter
import os
from txtfile import TxtFile


class Fitter:

    def __init__(self, name, function):
        self.name = name
        self.function = TF1(name, function)
        self.function.SetLineColor(2)  # red
        self.function.SetLineWidth(1)
        self.params = dict()
        self.virtualFitter = None
        self._covMatrix = None
        self._corrMatrix = None

    def setParam(self, index, name, startvalue=1):
        self.params[index] = {'name': name, 'startvalue': startvalue, 'value': 0, 'error': 0}
        self.function.SetParameter(index, startvalue)
        self.function.SetParName(index, name)

    def fit(self, graph, xstart, xend):
        graph.Fit(self.function, '', '', xstart, xend)
        self.virtualFitter = TVirtualFitter.GetFitter()
        for i in self.params:
            self.params[i]['value'] = self.virtualFitter.GetParameter(i)
            self.params[i]['error'] = self.virtualFitter.GetParError(i)
        n = len(self.params)
        self._covMatrix = [[self.virtualFitter.GetCovarianceMatrixElement(col, row) for row in xrange(n)] for col in xrange(n)]
        self._corrMatrix = [[self._covMatrix[col][row] / (self.params[col]['error'] * self.params[row]['error']) for row in xrange(n)] for col in xrange(n)]

    def getChisquare(self):
        return self.function.GetChisquare()

    def getNDF(self):
        return self.function.GetNDF()

    def getChisquareOverNDF(self):
        return self.getChisquare() / self.getNDF()
    
    def getCovMatrix(self):
        return self._covMatrix
        
    def getCovMatrixElem(self, col, row):
        return self._covMatrix[col][row]
        
    def getCorrMatrix(self):
        return self._corrMatrix
        
    def getCorrMatrixElem(self, col, row):
        return self._corrMatrix[col][row]

    def saveData(self, path):
        with TxtFile(path, 'w') as f:
            f.writeline('fitting info')
            f.writeline('============')
            f.writeline(TxtFile.CHISQUARE+ ':\t\t' + str(self.getChisquare()))
            f.writeline('NDF:\t' + str(self.getNDF()) + '')
            f.writeline(TxtFile.CHISQUARE + '/NDF:\t' + str(self.getChisquareOverNDF()))
            f.writeline('')
            f.writeline('parameters')
            f.writeline('==========')
            for i, param in self.params.iteritems():
                f.writeline('\t', str(i), param['name'], str(param['value']), TxtFile.PM, str(param['error']))
            f.writeline('')
            f.writeline('covariance matrix')
            f.writeline('=================')
            f.writelines('\t'.join(str(j) for j in i) + '\n' for i in self._covMatrix)
            f.writeline('')
            f.writeline('correlation matrix')
            f.writeline('==================')
            f.writelines('\t'.join(str(j) for j in i) + '\n' for i in self._corrMatrix)
            f.close()
