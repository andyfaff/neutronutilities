#!/usr/bin/python
from __future__ import division
import numpy as np
from scipy.optimize import minimize_scalar
import sys

def div(d1, d2, angle, L12 = 2850):
    '''
        returns the fractional angular resolution given a set of collimation conditions
        d1 - slit 1 opening (mm)
        d2 - slit 2 opening (mm)
        angle - angle of incidence (degrees)
    '''
    
    divergence = 0.68 * 0.68 * (d1 * d1 + d2 * d2) / L12 / L12
    return np.sqrt(divergence) / (angle * np.pi / 180)
    
    
