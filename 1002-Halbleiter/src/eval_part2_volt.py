#!/usr/bin/python2.7
import numpy as np
from functions import setupROOT, loadCSVToList, avgerrors
from halbleiter import P2SemiCon
from ROOT import TCanvas, TLegend, TGraph
from fitter import Fitter
from data import DataErrors
from txtfile import TxtFile


PRINTGRAPHS = False  # set False for quicker testing


def getParams():
    params = []
    params.append([[0.0044, 0, 1e-8, 17.5e-6, 5e-6], 5e-6, 27.5e-6])
    params.append([[0.0034, 0, 1e-8, 15e-6, 5e-6], 5e-6, 25e-6])
    params.append([[0.00275, 0, 2e-8, 13.5e-6, 4e-6], 5e-6, 25e-6])
    params.append([[0.002, 0, 2e-8, 12.5e-6, 3e-6], 5e-6, 25e-6])
    params.append([[-0.001, 0, 2e-8, 11e-6, 3e-6], 5e-6, 23e-6])
    params.append([[-0.002, 0, 3e-8, 11e-6, 3e-6], 6e-6, 15e-6])
    params.append([[-0.002, 0, 3e-8, 9e-6, 2e-6], 5e-6, 14.5e-6])
    params.append([[-0.0015, 0, 3e-8, 8.5e-6, 2e-6], 4.5e-6, 14e-6])
    params.append([[-0.003, 0, 3e-8, 9e-6, 2e-6], 4e-6, 13.75e-6])
    params.append([[-0.003, 0, 3e-8, 8e-6, 2e-6], 3.5e-6, 13.25e-6])
    params.append([[-0.003, 0, 3e-8, 8e-6, 2e-6], 3.25e-6, 13e-6])
    return params

def getVoltages():
    volts = []
    for i in range(11):
        data = P2SemiCon.fromPath('../data/part2/voltage/ALL%04.d/F%04dCH2.CSV' % (i, i))
        volts.append((abs(data.points[0][1]), P2SemiCon.UERROR))
    return volts

def evalVoltage(n, params):
    data = P2SemiCon.fromPath('../data/part2/voltage/ALL%04.d/F%04dCH1.CSV' % (n, n))
    g = data.makeGraph('g%d' % n, 'Zeit t / s', 'Spannung U / V')
    c = TCanvas('c%d' % n, '', 1280, 720)
    g.GetYaxis().SetTitleOffset(1.25)
    g.SetMarkerStyle(1)
    g.Draw('APX')

    fit = Fitter('f', 'pol1(0) + 1/(sqrt(2*pi*[4]^2))*gaus(2)')
    paramname = ['a', 'b', 'A', 'tm', 's']
    for i, param in enumerate(params[0]):
        fit.setParam(i, paramname[i], param)
    fit.fit(g, params[1], params[2])
    
    print(n)
    for key, param in fit.params.iteritems():
        print(param['name'], param['value'], param['error'])
    
    l = TLegend(0.15, 0.7, 0.3, 0.85)
    l.AddEntry(g, 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit Gausskurve', 'l')
    l.Draw()

    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/volt%02d.pdf' % n, 'pdf')

    return data, fit.params, fit.getCorrMatrix(), params[1], params[2]

def plotVoltages(graphs, voltages):
    c = TCanvas('cL', '', 1280, 720)
    l = TLegend(0.65, 0.3, 0.85, 0.85)
    l.AddEntry(0, 'Treibspannung', '')
    l.AddEntry(0,  '        U_{T} / V', '')
    first = True
    for i, g in enumerate(graphs):
        g.SetMarkerStyle(1)
        g.SetMarkerColor(int(round(51 + (100. - 51) / 11 * i)))
        g.GetXaxis().SetRangeUser(5e-6, 26e-6)
        if first:
            g.Draw('APX')
            g.SetMaximum(10e-3)
            g.SetMinimum(0)
            first = False
        else:
            g.Draw('PX')
        l.AddEntry(g, '%.2f' % voltages[i][0], 'p')
    l.Draw()
    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/voltages.pdf', 'pdf')
        
def fitXc(volts, times):
    listx, listsx = zip(*times)
    listy = []
    listsy = []
    for u, su in volts:  # convert u to 1/u
        y = 1. / u
        sy = su / (u ** 2)
        listy.append(y)
        listsy.append(sy)
    data = DataErrors.fromLists(listx, listy, listsx, listsy)

    c = TCanvas('cXc', '', 1280, 720)
    g = data.makeGraph('xc', 'Zeit t / s', 'reziproke Treibspannung 1/U_{T} / (1/V)')
    g.GetYaxis().SetTitleOffset(1.25)
    g.Draw('AP')
    
    fit = Fitter('fitXc', '1/[0] + [1]*x')
    fit.setParam(0, 'U0', -150)
    fit.setParam(1, 'm', 3e-3)
    fit.fit(g, 8e-6, 18e-6)
    fit.saveData('../calc/part2/volt_fit_xc.txt')
    
    l = TLegend(0.15, 0.7, 0.4, 0.85)
    l.AddEntry('xc', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit 1/U_{T} = m*t + 1/U_{0}', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'U_{0} = %.1e #pm %.0e' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.AddEntry(0, 'm = %.1e #pm %.0e' % (fit.params[1]['value'], fit.params[1]['error']), '')
    l.Draw()

    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/volt_fitXc.pdf', 'pdf')
    
    # calculate mu
    m, sm = fit.params[1]['value'], fit.params[1]['error']
    d, sd = 4, 0.005  # TODO check protocol for right values
    l = 30
    mu = m * l *d / 100  # /100 -> from mm in cm
    smu = mu * np.sqrt((sm/m)**2 + (sd/d)**2)
    with TxtFile('../calc/part2/volt_mu.txt', 'w') as f:
        f.writeline('\t', str(mu), str(smu))


def fitA(amps, times):
    listx, listsx = zip(*times)
    listy, listsy = zip(*amps)
    data = DataErrors.fromLists(listx, listy, listsx, listsy)

    c = TCanvas('cA', '', 1280, 720)
    g = data.makeGraph('A', 'Zeit t / s', 'A / V')
    g.SetMaximum(19e-9)
    g.Draw('AP')
    
    fit = Fitter('A', '[0]*exp(-(x)/[1])')
    fit.setParam(0, 'C', 5e-8)
    fit.setParam(1, 't_n', 45e-6)
    fit.fit(g, 7.5e-6, 18e-6)
    fit.saveData('../calc/part2/volt_fit_A.txt')
    
    l = TLegend(0.65, 0.65, 0.85, 0.85)
    l.AddEntry('A', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit y = C*exp(-t/#tau_{n})', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'C = %.2e #pm %.0e' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.AddEntry(0, '#tau_{n} = %.2e #pm %.0e' % (fit.params[1]['value'], fit.params[1]['error']), '')
    l.Draw()
    
    if PRINTGRAPHS:
        c.Update()
        c.Print('../img/part2/volt_fitA.pdf', 'pdf')
        

def fitSigma(sigs, times):
    listx, listsx = zip(*times)
    listy, listsy = zip(*sigs)
    listy = map(abs, listy)   # fits can yield negative sigma, because it only occurse to 
    data = DataErrors.fromLists(listx, listy, listsx, listsy)
    
    with TxtFile('../calc/part2/volt_sigmas.txt', 'w') as f:
        for x, y in zip(listx, listy):
            f.writeline('\t', str(x), str(y))

    c = TCanvas('cSigma', '', 1280, 720)
    g = data.makeGraph('Sigma', 'Zeit t / s', 'Standardabweichung #sigma / m')
    g.Draw('AP')
    
    fit = Fitter('fitS', 'sqrt(2*[0]*x)')
    fit.setParam(0, 'D_{n}', 2e-7)
    fit.fit(g, 8e-6, 18e-6)
    fit.saveData('../calc/part2/volt_fit_sigma.txt')
    
    l = TLegend(0.15, 0.7, 0.4, 0.85)
    l.AddEntry('Sigma', 'Messung', 'p')
    l.AddEntry(fit.function, 'Fit mit y = #sqrt{2*D_{n}*t}', 'l')
    l.AddEntry(0, 'Parameter:', '')
    l.AddEntry(0, 'D_{n} = %.3e #pm %.0e' % (fit.params[0]['value'], fit.params[0]['error']), '')
    l.Draw()
    
    if PRINTGRAPHS or True:
        c.Update()
        c.Print('../img/part2/volt_fitSigma.pdf', 'pdf')

def evalVoltages():
    params = getParams()
    volts = getVoltages()
    fittedData = []
    for i, param in enumerate(params):
        fittedData.append(evalVoltage(i, param))
        
    graphs = []  # list of graphs
    amps = []  # amplitudes
    times = []   # times
    sigs = []  # sigmas
    for data, param, corrMatrix, xmin, xmax in fittedData:
        # get data for further fits
        amps.append((param[2]['value'], param[2]['error']))
        times.append((param[3]['value'], param[3]['error']))
        sigs.append((param[4]['value'], param[4]['error']))

        # for plotting all data in one graph
        data.filterX(xmin, xmax)
        data.subtractUnderground(param[0]['value'], param[1]['value'], param[0]['error'], param[1]['error'], corrMatrix[0][1])
        data.addPoint(30e-6, 0, 0, 0)  # otherwise SetRangeUser() doesn't work
        graphs.append(data.makeGraph('g', 'Zeit t / s', 'Spannung U / V'))
    plotVoltages(graphs, volts)
    
    fitXc(volts, times)
    fitA(amps, times)
    fitSigma(sigs, times)


def main():
    setupROOT()
    evalVoltages()


if __name__ == "__main__":
    main()