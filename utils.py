#!/usr/bin/python
from __future__ import division
import numpy as np
import scipy.stats as ss
import scipy.integrate as spi

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
    calculate critical Q vector given SLD of super and subphases
    SLD1 - SLD of superphase (10^-6 A^-2)
    SLD2 - SLD of subphase (10^-6 A^-2)
    '''
    return np.sqrt(16. * np.pi * (SLD2 - SLD1) * 1.e-6)
    
def xraylam(energy):
    '''
    convert energy (keV) to wavelength (angstrom)
    '''
    return 12.398/ energy
    
def xrayenergy(wavelength):
    '''
    convert energy (keV) to wavelength (angstrom)
    '''
    return 12.398/ wavelength
    
def beamfrac(FWHM, length, angle):
    '''
    return the beam fraction intercepted by a sample of length length
    at sample tilt angle.
    The beam is assumed to be gaussian, with a FWHM of FWHM.
    '''
    height_of_sample = length * np.sin(np.radians(angle))
    beam_sd = FWHM / 2 / np.sqrt(2 * np.log(2))
    probability = 2. * (ss.norm.cdf(height_of_sample / 2. / beam_sd) - 0.5)
    return probability
    
def beamfrackernel(kernelx, kernely, length, angle):
    '''
    return the beam fraction intercepted by a sample of length length
    at sample tilt angle.
    The beam has the shape 'kernel', a 2 row array, which gives the PDF for the beam
    intensity as a function of height. The first row is position, the second row is
    probability at that position
    '''
    height_of_sample = length * np.sin(np.radians(angle))
    total = spi.simps(kernely, kernelx)
    lowlimit = np.where(-height_of_sample / 2. >= kernelx)[0][-1]
    hilimit = np.where(height_of_sample / 2. <= kernelx)[0][0]
    
    area = spi.simps(kernely[lowlimit: hilimit + 1], kernelx[lowlimit: hilimit + 1])
    return area / total