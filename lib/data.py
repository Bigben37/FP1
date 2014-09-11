#!/usr/bin/python2.7
from ROOT import TGraph
import array

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
                print("Data.loadData() not in scope! Please implement. ")
        return data

    @classmethod
    def fromLists(cls, x, y):
        if len(x) == len(y):
            data = cls()
            data.setXY(x, y)
            return data
        else:
            print('Data.fromLists():ERROR - lists have to be the same length')
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