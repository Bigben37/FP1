#!/usr/bin/python2.7
"""The Fitter class is a link to ROOTs TFitter, but enhanced with better management of parameters and covariant / correlation matrix"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from ROOT import TF1, TVirtualFitter    # ROOT library
from txtfile import TxtFile             # basic output to txt files, can be found the /lib directory


class Fitter:
    """This class is a tool for fitting experimental data"""
    
    def __init__(self, name, function):
        """Constructor, sets some constants for fitting function and initializes fields
        
        Arguments:
        name     -- ROOT internal name of function
        function -- function to fit, use conventions from ROOT
        """
        self._function = TF1(name, function)
        self._function.SetLineColor(2)  # red
        self._function.SetLineWidth(1)
        self.params = dict()
        self.virtualFitter = None
        self._covMatrix = None
        self._corrMatrix = None

    def setParam(self, index, name, startvalue=1):
        """initializes parameter
        
        Arguments:
        index      -- index of parameter (has to be the same as in the function of constructor)
        name       -- name of parameter
        startvalue -- start value of parameter for fit (default = 1)
        """
        self.params[index] = {'name': name, 'startvalue': startvalue, 'value': 0, 'error': 0}
        self._function.SetParameter(index, startvalue)
        self._function.SetParName(index, name)

    def fit(self, graph, xstart, xend):
        """computes fit and stores calculated parameters with errors in parameter dict. 
        Also extracts covariance matrix and calculates correlation matrix
        
        Arguments:
        graph  -- an instance of ROOTs TGraph with data to fit
        xstart -- start value for x interval  
        xend   -- end value for x interval
        """
        graph.Fit(self._function, '', '', xstart, xend)
        self.virtualFitter = TVirtualFitter.GetFitter()
        for i in self.params:
            self.params[i]['value'] = self.virtualFitter.GetParameter(i)
            self.params[i]['error'] = self.virtualFitter.GetParError(i)
        n = len(self.params)
        self._covMatrix = [[self.virtualFitter.GetCovarianceMatrixElement(col, row) for row in xrange(n)] for col in xrange(n)]
        self._corrMatrix = [[self._covMatrix[col][row] / (self.params[col]['error'] * self.params[row]['error']) for row in xrange(n)] for col in xrange(n)]

    def getFunction(self):
       """returns fit function"""
       return self._function
   
    function = property(getFunction)

    def getChisquare(self):
        """returns chi^2 of fit"""
        return self._function.GetChisquare()

    def getDoF(self):
        """returns degrees of freedom of fit"""
        return self._function.GetNDF()

    def getChisquareOverDoF(self):
        """returns chi^2 over degrees of freedom of fit"""
        return self.getChisquare() / self.getDoF()
    
    def getCovMatrix(self):
        """returns covariance matrix of fit"""
        return self._covMatrix
        
    def getCovMatrixElem(self, col, row):
        """returns entry of covariance matrix
        
        Arguments:
        col -- column of element
        row -- row of element
        """
        return self._covMatrix[col][row]
        
    def getCorrMatrix(self):
        """returns correlation matrix"""
        return self._corrMatrix
        
    def getCorrMatrixElem(self, col, row):
        """returns entry of correlation matrix
        
        Arguments:
        col -- column of element
        row -- row of element
        """
        return self._corrMatrix[col][row]

    def saveData(self, path, mode='w', enc='utf-8'):
        """saves fitting info (chi^2, DoF, chi^2/DoF, paramters with values and errors, covariance and correlation matrix)
        
        Arguments:
        path -- relative path to file
        mode -- write mode (usually 'w' for overwriting or 'a' for appending)
        enc  -- encoding (default = 'utf-8')
        """
        with TxtFile.fromRelPath(path, mode) as f:
            f.writeline('fitting info')
            f.writeline('============')
            f.writeline(TxtFile.CHISQUARE+ ':\t\t' + str(self.getChisquare()))
            f.writeline('NDF:\t' + str(self.getDoF()) + '')
            f.writeline(TxtFile.CHISQUARE + '/DoF:\t' + str(self.getChisquareOverDoF()))
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
            f.writeline()
            f.close()
