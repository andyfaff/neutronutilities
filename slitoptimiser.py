#!/usr/bin/python
from __future__ import division
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

#slit1-slit2 distance (mm)
L12 = 1402.6
#slit2 - sample distance (mm)
L2S = 330.2
#sample - S5 distance (mm)
LS5 = 266.7
#sample - S6 distance (mm)
LS6 = 1155.7
#sample detector (mm) - from ANDR paper
LSD = 1358

def height_of_beam_after_d2(d1, d2, distance):
    '''
        Calculate total width of beam a given distance away from the last collimation slit. 
        d1 - opening of first collimation slit
        d2 - opening of second collimation slit
        distance - distance from last slit to a given position
        Units - equivalent distances (inches, mm, light years)
        
    '''
    
    dtheta = (d1 + d2) / 2 / L12
    return (dtheta * distance * 2) + d2

def slitoptimiser(footprint, resolution, angle = 1.):
    '''
        Optimise slit settings for a given angular resolution, and a given footprint. 
        
        footprint - maximum footprint onto sample (mm)
        resolution - fractional dtheta/theta resolution (FWHM)
        angle      - optional, angle of incidence in degrees
        
        Note that this function is hardcoded for given instrument distances.
    '''
    
    print '_____________________________________________'
    print 'FOOTPRINT calculator - Andrew Nelson 2013'
    print 'INPUT'
    print 'footprint:', footprint, 'mm'
    print 'fractional angular resolution (FWHM):', resolution
    print 'theta:', angle, 'degrees'
    
    d1star = lambda d2star : np.sqrt(1 - np.power(d2star, 2))
    L1star = 0.68 * footprint/L12/resolution
    
    gseekfun = lambda d2star : np.power((d2star + L2S/L12 * (d2star + d1star(d2star))) - L1star, 2)
    
    res = minimize_scalar(gseekfun, method = 'bounded', bounds = (0, 1))
    if res['success'] is False:
        print 'ERROR: Couldnt find optimal solution, sorry'
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
    
    d1 = optimal_d1star * resolution / 0.68 * angle * np.pi / 180 * L12
    d2 = d1 * multfactor

    print '\nOUTPUT'
    
    if multfactor == 1:
        print 'Your desired resolution results in a smaller footprint than the sample supports.'
        suggested_resolution =  resolution * footprint / (height_of_beam_after_d2(d1, d2, L2S) / (angle * np.pi / 180))
        print 'You can increase flux using a resolution of', suggested_resolution, 'and still keep the same footprint.'

    
    height_at_S5 = height_of_beam_after_d2(d1, d2, L2S + LS5)
    height_at_S6 = height_of_beam_after_d2(d1, d2, L2S + LS6)
    height_at_detector = height_of_beam_after_d2(d1, d2, L2S + LSD)
    actual_footprint = height_of_beam_after_d2(d1, d2, L2S) / (angle * np.pi / 180)

    print '\nd1', d1, 'mm'
    print 'd2', d2, 'mm'
    print '\nfootprint:', actual_footprint, 'mm'
    print 'height at S5:', height_at_S5, 'mm'
    print 'height at S6:', height_at_S6, 'mm'
    print 'height at detector:', height_at_detector, 'mm'
    print '\n[d2star', optimal_d2star, ']'
    print '_____________________________________________'
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage:\n\
            python slitoptimiser.py footprint relative_resolution [angle]\n\
            python slitoptimiser.py 50 0.04 [2]'
    slitoptimiser(*[float(val) for val in sys.argv[1:]])