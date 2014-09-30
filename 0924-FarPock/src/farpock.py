from data import DataErrors
import os

class PockData(DataErrors):
    
    def __init__(self):
        super(PockData, self).__init__()
        self.ycol = 1
    
    @classmethod
    def fromPath(cls, path, ycol):
        data = cls()
        data.path = path
        data.ycol = ycol
        if path:
            try:
                data.loadData()
            except NameError:
                print(data.__class__.__name__ + ".loadData() not in scope! Please implement. ")
        return data
    
    #def loadData(self):
        #print(self.ycol)
        
    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            firstline = True
            for row in f:
                if firstline:
                    firstline = False
                else:
                    row = row.strip().split('\t')                
                    self.addPoint(float(row[0]), float(row[self.ycol]), 0,0)
                
