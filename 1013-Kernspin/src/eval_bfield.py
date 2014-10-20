#!/usr/bin/python2.7
from functions import setupROOT, loadCSVToList  # make sure to add ../lib to your project path or copy file from there
from kernspin import ERRORS
from data import DataErrors
from ROOT import TCanvas


def evalBx():
    datalist = loadCSVToList('../data/01-B-x.txt')
    x, y = zip(*datalist)
    sx = [ERRORS['x']] * len(x)
    sy = [ERRORS['B']] * len(y)
    data = DataErrors.fromLists(x, y, sx, sy)

    c = TCanvas('cBx', '', 1280, 720)
    g = data.makeGraph('gBx', 'Tiefe x / mm', 'Magnetfeld B / mT')
    g.Draw('AP')
    c.Update()
    c.Print('../img/01-B-x.pdf', 'pdf')
    
    g.GetXaxis().SetRangeUser(3, 37)
    g.SetMinimum(395)
    g.SetMaximum(410)
    c.Update()
    c.Print('../img/01-B-x-zoom.pdf', 'pdf')
    


def evalBI():
    # load from low
    datalist = loadCSVToList('../data/02-I-B-low.txt')
    x, y = zip(*datalist)
    sx = [ERRORS['I']] * len(x)
    sy = [ERRORS['B']] * len(y)
    low = DataErrors.fromLists(x, y, sx, sy)
    # load from up
    datalist = loadCSVToList('../data/02-I-B-up.txt')
    x, y = zip(*datalist)
    sx = [ERRORS['I']] * len(x)
    sy = [ERRORS['B']] * len(y)
    up = DataErrors.fromLists(x, y, sx, sy)

    c = TCanvas('c', '', 1280, 720)
    glow = low.makeGraph('gIBlow', 'Stromst#ddot{a}rke I / A', 'Magnetfeld B / mT')
    glow.Draw('AP')
    gup = up.makeGraph('gIBlow', 'Stromst#ddot{a}rke I / A', 'Magnetfeld B / mT')
    gup.SetMarkerColor(2)
    gup.SetLineColor(2)
    gup.Draw('P')

    c.Update()
    c.Print('../img/02-BI.pdf', 'pdf')


def main():
    evalBx()
    evalBI()

if __name__ == '__main__':
    setupROOT()
    main()
