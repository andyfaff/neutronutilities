#!/usr/bin/python

import numpy as np
from scipy.optimize import minimize_scalar
import sys

'''
Script to estimate optimum slit settings.

For a given footprint and angle combination there is a maximum angular resolution that can be achieved whilst keeping the slits equal in size.

Alternatively, for a given angle and a given angular resolution find the optimum slit settings to maximise the footprint/intensity on the sample

See equations 11-14 in:
de Haan, V.-O.; de Blois, J.; van der Ende, P.; Fredrikze, H.; van der Graaf, A.; Schipper, M.; van Well, A. A. & J., v. d. Z. ROG, the neutron reflectometer at IRI Delft Nuclear Instruments and Methods in Physics Research A, 1995, 362, 434-453

Andrew Nelson - 2013

'''

def height_of_beam_after_dx(d1, d2, L12, distance):
    '''
        Calculate total width of beam a given distance away from a collimation slit. 
        if distance >= 0, then it's taken to be the distance after d2.
        if distance < 0, then it's taken to be the distance before d1.
        
        d1 - opening of first collimation slit
        d2 - opening of second collimation slit
        distance - distance from first or last slit to a given position
        Units - equivalent distances (inches, mm, light years)
        
    '''
    
    dtheta = (d1 + d2) / 2 / L12
    if distance >= 0:
        return (dtheta * distance * 2) + d2
    else:
        return (dtheta * abs(distance) * 2) + d1
        
    
def actual_footprint(d1, d2, L12, L2S, angle):
    return height_of_beam_after_dx(d1, d2, L12, L2S) / np.radians(angle)

def slitoptimiser(footprint,
                     resolution, 
                     angle = 1., 
                      L12 = 2859.5,
                      L2S = 276,
                      LS4 = 290.5,
                      LSD = 2500,
                      verbose = True):
    '''
        Optimise slit settings for a given angular resolution, and a given footprint. 
        
        footprint - maximum footprint onto sample (mm)
        resolution - fractional dtheta/theta resolution (FWHM)
        angle      - optional, angle of incidence in degrees
        
        #slit1-slit2 distance (mm)
        L12 = 2859.5
        #slit2 - sample distance (mm)
        L2S = 276
        #sample - S5 distance (mm)
        LS4 = 290.5
        #sample detector (mm)
        LSD = 2500        
    '''
    if verbose:
        print('_____________________________________________')
        print('FOOTPRINT calculator - Andrew Nelson 2013')
        print('INPUT')
        print('footprint:', footprint, 'mm')
        print('fractional angular resolution (FWHM):', resolution)
        print('theta:', angle, 'degrees')
    
    d1star = lambda d2star : np.sqrt(1 - np.power(d2star, 2))
    L1star = 0.68 * footprint/L12/resolution
    
    gseekfun = lambda d2star : np.power((d2star + L2S/L12 * (d2star + d1star(d2star))) - L1star, 2)
    
    res = minimize_scalar(gseekfun, method = 'bounded', bounds = (0, 1))
    if res['success'] is False:
        print('ERROR: Couldnt find optimal solution, sorry')
        return None
        
    optimal_d2star = res['x']
    optimal_d1star = d1star(optimal_d2star)
    if optimal_d2star > optimal_d1star:
        #you found a minimum, but this may not be the optimum size of the slits.
        multfactor = 1
        optimal_d2star = 1/np.sqrt(2)   
        optimal_d1star = 1/np.sqrt(2)
    else:
        multfactor = optimal_d2star / optimal_d1star
    
    d1 = optimal_d1star * resolution / 0.68 * np.radians(angle) * L12
    d2 = d1 * multfactor
    
    height_at_S4 = height_of_beam_after_dx(d1, d2, L12, L2S + LS4)
    height_at_detector = height_of_beam_after_dx(d1, d2, L12, L2S + LSD)
    actual_footprint = height_of_beam_after_dx(d1, d2, L12, L2S) / np.radians(angle)

    if verbose:
        print('OUTPUT')
        if multfactor == 1:
            print('Your desired resolution results in a smaller footprint than the sample supports.')
            suggested_resolution =  resolution * footprint / (height_of_beam_after_dx(d1, d2, L21, L2S) / np.radians(angle))
            print('You can increase flux using a resolution of', suggested_resolution, 'and still keep the same footprint.')
        print('d1', d1, 'mm')
        print('d2', d2, 'mm')
        print('footprint:', actual_footprint, 'mm')
        print('height at S4:', height_at_S4, 'mm')
        print('height at detector:', height_at_detector, 'mm')
        print('[d2star', optimal_d2star, ']')
        print('_____________________________________________')

    return d1, d2
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:\n\
            python slitoptimiser.py footprint relative_resolution [angle]\n\
            python slitoptimiser.py 50 0.04 [2]')
    else:
        slitoptimiser(*[float(val) for val in sys.argv[1:]])
