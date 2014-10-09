#!/usr/bin/python2.7
from functions import setupROOT, avgerrors  # make sure to add ../lib to your project path or copy file from there
from ringlaser import X0Data
from ROOT import TCanvas, TLegend, TLine
from fitter import Fitter  # make sure to add ../lib to your project path or copy file from there
from txtfile import TxtFile  # make sure to add ../lib to your project path or copy file from there
import numpy as np