#!/usr/bin/python
from __future__ import division
import numpy as np
import sys

def div(d1, d2, angle, L12 = 2859):
    '''
        returns the fractional angular resolution (FWHM) given a set of collimation conditions
        d1 - slit 1 opening (mm)
        d2 - slit 2 opening (mm)
        angle - angle of incidence (degrees)
    '''
    
    divergence = 0.68 * 0.68 * (d1 * d1 + d2 * d2) / L12 / L12
    return np.sqrt(divergence) / (angle * np.pi / 180)
    
def qcalc(angle, wavelength):
    '''
    calculate Q given angle of incidence and wavelength
    angle - angle of incidence (degrees)
    wavelength -  wavelength of radiation (Angstrom)
    '''
    return 4 * np.pi * np.sin(angle * np.pi / 180) / wavelength

def wavelength(q, angle):
    '''
    calculate wavelength given Q vector and angle
    q - wavevector (A^-1)
    angle - angle of incidence (degrees)
    '''
    return  4. * np.pi * np.sin(angle * np.pi / 180.)/q

def angle(q, wavelength):
    '''
    calculate angle given Q and wavelength
    q - wavevector (A^-1)
    wavelength -  wavelength of radiation (Angstrom)
    '''
    return  np.asin(q / 4. / np.pi * wavelength) * 180 / np.pi
    
def qcrit(SLD1, SLD2):
    '''
    '''
    return np.sqrt(16. * np.pi * (SLD2 - SLD1))