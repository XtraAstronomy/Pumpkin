'''
Calculate Virial Radius given M_500
'''
import numpy as np
import astropy.constants as cst
def H_sq(H_0,Omega_M,Omega_L,z):
    Omega_tot = Omega_L+Omega_M
    Hsq = H_0**2*(Omega_M*(1+z)**3+(1-Omega_tot)*(1+z)**2+Omega_L)
    return Hsq

def calc_vir_rad(M_500,z):
    '''
    Calculate virial radius
    params:
        M_500 - Virial Mass in Solar Masses
        z - Redshift
    '''
    H_0 = 70 #Hubble Constant
    Omega_M = .3 #Omega Matter
    Omega_L = 0.7 #Omega Lambda
    H_z = H_sq(H_0,Omega_M,Omega_L,z)
    rad = np.cbrt((cst.G.value*M_500)/(250*H_z))
    return rad
