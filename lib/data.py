#!/usr/bin/python2.7
from ROOT import TGraph, TGraphErrors
import array
import numpy as np
from txtfile import TxtFile

class Data(object):

    def __init__(self):
        self.path = ''
        self._points = []

    def getPoints(self):
        return self._points
    
    def setPoints(self, points):
        self._points = points
        
    points = property(getPoints, setPoints)

    def getX(self):
        return list(zip(*self._points)[0])
        
    def getY(self):
        return list(zip(*self._points)[1])
    
    def getPoint(self, i):
        if i < len(self._points):
            return self._points[i]
        else:
            return None

    def addPoint(self, x, y):
        self._points.append((x, y))
        
    def setXY(self, xlist, ylist):
        if len(xlist) == len(ylist):
            self._points = zip(xlist, ylist)
        else:
            print('Data.setXY(x, ypyth):ERROR - lists have to be the same length')
            
    def getLength(self):
        return len(self._points)

    @classmethod
    def fromPath(cls, path):
        data = cls()
        data.path = path
        if path:
            try:
                data.loadData()
            except NameError:
                print(data.__class__.__name__ + ".loadData() not in scope! Please implement. ")
        return data

    @classmethod
    def fromLists(cls, x, y):
        if len(x) == len(y):
            data = cls()
            data.setXY(x, y)
            return data
        else:
            print('Data.fromLists(x, y):ERROR - lists have to be the same length')
            return None

    def makeGraph(self, name='', xtitle='', ytitle=''):
        x = self.getX()
        y = self.getY()
        graph = TGraph(self.getLength(), array.array('f', x), array.array('f', y))
        graph.SetName(name)
        graph.SetMarkerColor(1)
        graph.SetMarkerStyle(5)
        graph.SetTitle("")
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle(ytitle)
        graph.GetYaxis().CenterTitle()
        return graph
    
    def saveData(self, title, path, mode, encoding=''):
        with TxtFile(path, mode, encoding) as f:
            f.writeline(title)
            f.writeline('='*len(title))
            for point in self.points:
                f.writeline('\t', *point)
                
    def __add__(self, other):
        if isinstance(other, Data):
            if self.getLength() == other.getLength():
                y = []
                ys = self.getY()
                yo = other.getY()
                for i in range(self.getLength()):
                    y.append(ys[i] + yo[i])
                return Data.fromLists(self.getX(), y)
            else:
                return NotImplemented
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Data):
            if self.getLength() == other.getLength():
                y = []
                ys = self.getY()
                yo = other.getY()
                for i in range(self.getLength()):
                    y.append(ys[i] - yo[i])
                return Data.fromLists(self.getX(), y)
            else:
                return NotImplemented
        else:
            return NotImplemented
        

class DataErrors(object):

    def __init__(self):
        self.path = ''
        self._points = []

    def getPoints(self):
        return self._points
    
    def setPoints(self, points):
        self._points = points
        
    points = property(getPoints, setPoints)

    def getX(self):
        return list(zip(*self._points)[0])
        
    def getY(self):
        return list(zip(*self._points)[1])
    
    def getEX(self):
        return list(zip(*self._points)[2])
    
    def getEY(self):
        return list(zip(*self._points)[3])    
    
    def getPoint(self, i):
        if i < len(self._points):
            return self._points[i]
        else:
            return None

    def addPoint(self, x, y, ex, ey):
        self._points.append((x, y, ex, ey))
        
    def setXY(self, xlist, ylist, exlist, eylist):
        if len(xlist) == len(ylist) == len(exlist) == len(eylist):
            self._points = zip(xlist, ylist, exlist, eylist)
        else:
            print('Data.setXY(x, y, ex, ey):ERROR - lists have to be the same length')
            
    def getLength(self):
        return len(self._points)

    @classmethod
    def fromPath(cls, path):
        data = cls()
        data.path = path
        if path:
            try:
                data.loadData()
            except NameError:
                print("Data.loadData() not in scope! Please implement. ")
        return data

    @classmethod
    def fromLists(cls, x, y, ex, ey):
        if len(x) == len(y) == len(ex) == len(ey):
            data = cls()
            data.setXY(x, y, ex, ey)
            return data
        else:
            print('Data.fromLists():ERROR - lists have to be the same length')
            return None

    def makeGraph(self, name='', xtitle='', ytitle=''):
        x = self.getX()
        y = self.getY()
        ex = self.getEX()
        ey = self.getEY()
        graph = TGraphErrors(self.getLength(), array.array('f', x), array.array('f', y), array.array('f', ex), array.array('f', ey))
        graph.SetName(name)
        graph.SetMarkerColor(1)
        graph.SetMarkerStyle(5)
        graph.SetTitle("")
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle(ytitle)
        graph.GetYaxis().CenterTitle()
        return graph
    
    def setXErrorAbs(self, error):
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], error, self.points[i][3])
            
    def setXErrorRel(self, relerror):
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][0]*relerror, self.points[i][3])
            
    def setXErrorFunc(self, f):
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], f(self.points[i][0]), self.points[i][3])
    
    def setYErrorAbs(self, error):
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][2], error)
            
    def setYErrorRel(self, relerror):
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][2], self.points[i][1]*relerror)
            
    def setYErrorFunc(self, f):
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][2], f(self.points[i][1]))
            
    def saveDataToLaTeX(self, thead, format, caption, label, path, mode, encoding='utf-8'):
        i = '  '  # intendation
        with TxtFile(path, mode, encoding) as f:
            f.writeline('\\begin{table}[H]')
            f.writeline('\\caption{' + caption + '}')
            f.writeline('\\begin{center}')
            f.writeline('\\begin{tabular}{' + '|c' * len(self.points[0])  + '|}')
            f.writeline(i + '\hline')
            f.writeline(i + ' & '.join(thead) + ' \\\\ \hline ')
            for point in self.points:
                f.writeline(i + ' & '.join(format) % (point[0], point[2], point[1], point[3]) + ' \\\\ \hline')
            f.writeline('\\end{tabular}')  
            f.writeline('\\end{center}')    
            f.writeline('\\label{' + label  + '}')  
            f.writeline('\\end{table}')
    
    def __add__(self, other):
        if isinstance(other, DataErrors):
            if self.getLength() == other.getLength():
                y = []
                yerror = []
                ys = self.getY()
                yse = self.getEY()
                yo = other.getY()
                yoe = other.getYE()
                for i in range(self.getLength()):
                    y.append(ys[i] + yo[i])
                    yerror.append(np.sqrt((yse[i])**2 + (yoe[i])**2))
                return DataErrors.fromLists(self.getX(), y, [0] * self.getLength(), yerror)
            else:
                return NotImplemented
        else:
            return NotImplemented
        
    def saveData(self):
        pass

    def __sub__(self, other):
        if isinstance(other, DataErrors):
            if self.getLength() == other.getLength():
                y = []
                yerror = []
                ys = self.getY()
                yse = self.getEY()
                yo = other.getY()
                yoe = other.getEY()
                for i in range(self.getLength()):
                    y.append(ys[i] - yo[i])
                    yerror.append(np.sqrt((yse[i])**2 + (yoe[i])**2))
                print(yerror)
                return DataErrors.fromLists(self.getX(), y, [0] * self.getLength(), yerror)
            else:
                return NotImplemented
        else:
            return NotImplemented