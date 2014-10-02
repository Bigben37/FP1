#!/usr/bin/python2.7
from ROOT import gROOT, gStyle, TCanvas, TF1

def makeColorGraph():
    CMAX = 100

    c = TCanvas('c', '', 1280, 720)
    funcs = []
    for i in xrange(1, CMAX + 1):
        f = TF1("f%d" % i, "%d" % i, 0, 10)
        f.SetLineColor(i)
        f.GetYaxis().SetRangeUser(0, CMAX)
        funcs.append(f)
        
    first = True
    for f in funcs:
        if first:
            f.Draw()
            first = False
        else:
            f.Draw('LSAME')

    c.Update()
    c.Print('./colors.pdf', 'pdf')
    

def main():
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)
    makeColorGraph()

if __name__ == "__main__":
    main()