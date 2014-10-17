from data import DataErrors
import os

class HanleData(DataErrors):
    def __init__(self):
        super(HanleData, self).__init__()
        self.channel = 1
        
    @classmethod
    def fromPath(cls, path, channel):
        data = cls()
        data.path = path
        data.channel = channel
        if path:
            data.loadData()
        return data
    
    def loadData(self):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, self.path))
        isHeader = True
        with open(p, 'r') as f:
            for row in f:
                if isHeader:
                    isHeader = False
                else:
                    data = map(lambda x: float(x.replace(',', '.')), row.strip().split('\t'))
                    x = data[0]
                    y = data[self.channel]
                    sx = x * 0.01
                    sy = y * 0.01
                    self.addPoint(x, y, sx, sy)
                    

    def convertTimeToB(self, fit):
        for i in xrange(self.getLength()):
            x, y, sx, sy = self.getPoint(i)
            x = fit.Eval(x) * 3.363e-4 * 1000 # in mT
            sx = x * 0.01
            self.points[i] = (x, y, sx, sy)
    
def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)