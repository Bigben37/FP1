#!/usr/bin/python2.7
from ROOT import TCanvas, TLegend, gPad

# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from data import DataErrors
from functions import setupROOT, loadCSVToList
# ========================================================================


def main():
    squid = loadCSVToList('../calc/bfields_leiterschleife_fit.txt')
    theo = loadCSVToList('../calc/bfields_leiterschleife_theo.txt')
    resistors = loadCSVToList('../data/resistors.txt')
    x = [u / r for r, u in resistors]
    sx = [0.01 / r for r, u in resistors]
    ysquid, sysquid = zip(*squid)
    ytheo, sytheo = zip(*theo)

    c = TCanvas('c', '', 1280, 720)

    theoData = DataErrors.fromLists(x, ytheo, sx, sytheo)
    gTheo = theoData.makeGraph('gTheo', 'Strom I / A', 'Magnetfeld B_{z} / T')
    gTheo.SetMarkerColor(2)
    gTheo.SetLineColor(2)
    gTheo.Draw('AP')

    squidData = DataErrors.fromLists(x, ysquid, sx, sysquid)
    gSquid = squidData.makeGraph('gSquid', 'Strom I / A', 'Magnetfeld B_{z} / T')
    gSquid.Draw('P')

    l = TLegend(0.15, 0.7, 0.5, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(gSquid, 'gemessene Magnetfeldst#ddot{a}rke B_{z}', 'p')
    l.AddEntry(gTheo, 'theoreitsche Magnetfeldst#ddot{a}rke B_{z}', 'p')
    l.Draw()

    c.Update()
    c.Print('../img/compare.pdf', 'pdf')

    c.SetLogy()
    c.SetLogx()
    c.Update()
    c.Print('../img/compare_loglog.pdf', 'pdf')


if __name__ == '__main__':
    setupROOT()
    main()
