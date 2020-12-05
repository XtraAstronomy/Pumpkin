'''
Calculate Virial Radius given M_500
'''
import os
import math
from os import path
import pandas as pd
from ASCalc import calculate_angle
import astropy.constants as cst
import numpy as np
import scipy.integrate as spi
import scipy.constants as spc
from astropy.cosmology import Planck13 as cosmo
from astropy import constants as const

#----------------------FUNCTIONS-------------------------#
dens_const = 500


def Energy_func_inv(z,Omega_rel,Omega_mass,Omega_lam,Omega_k):
    return 1/(np.sqrt(Omega_rel*(1+z)**4+Omega_mass*(1+z)**3+Omega_k*(1+z)**2+Omega_lam))

def calc_ang(z,l):
    Omega_rel = cosmo.Onu0
    Omega_mass = cosmo.Om0
    Omega_lam = cosmo.Ode0
    Omega_K = 1-Omega_mass-Omega_lam
    Hubble_const = cosmo.H0.value
    d_H = spc.c/Hubble_const
    #print(spi.quad(Energy_func_inv,0,z,args=(Omega_rel,Omega_mass,Omega_lam,Omega_K))[0])
    d_C = d_H*spi.quad(Energy_func_inv,0,z,args=(Omega_rel,Omega_mass,Omega_lam,Omega_K))[0]
    if Omega_K > 0:
        d_M = (d_H/np.sqrt(Omega_K))*np.sinh(np.sqrt(Omega_K)*d_C/d_H)
    if Omega_K == 0:
        d_M = d_C
    if Omega_K < 0:
        d_M = (d_H/np.sqrt(np.abs(Omega_K)))*np.sin(np.sqrt(np.abs(Omega_K))*d_C/d_H)
    d_A = d_M/(1+z)
    theta_rad = l/d_A
    theta = theta_rad*(648000/np.pi) #degree
    # print('Virial Radius in arcseconds: %.2f'%theta)
    return theta


def Energy_func(z):
    Omega_mass = 0.3#cosmo.Om0
    Omega_lam = 0.7#cosmo.Ode0
    return Omega_mass*(1+z)**3+Omega_lam

def calc_crit_dens(redshift):
    E = Energy_func(redshift)
    Hubble_const = cosmo.H0.to('km/(km s)')
    rho = (3*Hubble_const**2*E)/(8*math.pi*const.G)
    return rho

def calc_vir_rad(M_500,redshift):
    '''
    Calculate virial radius
    params:
        M_500 - Virial Mass in Solar Masses
        z - Redshift
    '''
    M = M_500*const.M_sun
    crit_dens = calc_crit_dens(redshift)
    R = np.cbrt((3*M)/(4*np.pi*crit_dens*dens_const)).to('kpc').value # Value in kpc
    print('  Virial Radius: %.2f kpc'%R)
    return R
