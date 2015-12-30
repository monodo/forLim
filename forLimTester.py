# -*- coding: utf-8 -*-
"""
Created on Fri Dec 04 11:05:43 2015

Description:

forLimTester.py enables to run the forest delimitation algorithm directly from 
a python call without running QGIS. (a proper osgeo/qgis/python environment 
is required to run this) Both convolution and triangulation methods can be 
chosen.

This is dedicaced to a development/debugging purpose.

Usage:

    forLimTester.py

Example:

    Import forLimTester
    
    forLimTester
    
@author: Arnaud Poncet-Montanges
"""
# Import both methods scripts
#import convolutionMethod
import delaunayMethod

def main():
    print 'Hi, welcome to forLim in console mode'
    
    options = {}
    options['src'] = 'C:\\Users\\Nono\\workspace\\input'
    options['dst'] = 'C:\\Users\\Nono\\workspace\\output'
    options['MinHeightThres'] = 2
    options['WinRad'] = 4
    options['method'] = 2
    options['suffix'] = "cimes"
    
    if options['method'] == 1:
        #convolutionMethod.main(options)
        print 'You have chosen the convolution method'
        print 'It is not yet implemented for testing'
    else:
        delaunayMethod.main(options)

if __name__ == "__main__":
    main()

__author__ = "Arnaud Poncet-Montanges, SFFN, Couvet (CH)"
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Arnaud Poncet-Montanges"
__email__ = "arnaudponcetmontanges@gmail.com"
__status__ = "Development"
