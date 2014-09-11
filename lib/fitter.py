#!/usr/bin/python2.7
from ROOT import TF1, TVirtualFitter, TMatrixD
import os, codecs

class Fitter:
    
    def __init__(self, name, function):
        self.name = name
        self.function = TF1(name, function)
        self.function.SetLineColor(2)  # red
        self.function.SetLineWidth(1)
        self.params = dict()
        self.virtualFitter = None
        self.matrix = None
        
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
        self.matrix =[[self.virtualFitter.GetCovarianceMatrixElement(col, row) for row in xrange(n)] for col in xrange(n)]
        
    def getChisquare(self):
        return self.function.GetChisquare()
    
    def getNDF(self):
        return self.function.GetNDF()
    
    def getChisquareOverNDF(self):
        return self.getChisquare() / self.getNDF()
    
    def saveData(self, path):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, path))
        if not os.path.exists(p):
            os.mkdir(os.path.dirname(p))
            open(p, 'a').close()
        with codecs.open(p, 'w', 'utf-8') as f:
            f.write('fitting info\n')
            f.write('============\n')
            f.write(unichr(0x1D712) + unichr(0x00B2) + ':\t\t' + str(self.getChisquare()) + '\n')
            f.write('NDF:\t' + str(self.getNDF()) + '\n')
            f.write(unichr(0x1D712) + unichr(0x00B2) + '/NDF:\t' + str(self.getChisquareOverNDF()) + '\n')
            f.write('\n')
            f.write('parameters\n')
            f.write('==========\n')
            for i, param in self.params.iteritems():
                #f.write(str(i) + '\t' + param['name'] + '\t' + str(param['value']) + '\t(+-)\t' + str(param['error']) + '\n')
                f.write('\t'.join([str(i), param['name'], str(param['value']), unichr(0x00B1), str(param['error'])]) + '\n')
            f.write('\n')
            f.write('covariance matrix\n')
            f.write('=================\n')
            f.writelines('\t'.join(str(j) for j in i) + '\n' for i in self.matrix)
            #TODO create and print correlation coefficient matrix
            f.close()