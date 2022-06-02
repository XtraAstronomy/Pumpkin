'''
Calculate all additional parameters for each annulus:
    - Electron Density
    - Pressure
    - Entropy
    - Cooling time
'''
import numpy as np
from Misc.Classes import annulus


def PostProcess(annuli_data,redshift,out_dir):
    '''
    Create the csv files containing fit information and errors
    :param annuli_data - list of annulus class instances
    :param redshift - redshift of cluster
    :param out_dir - path to output annuli data
    '''
    file_to_write = open("Fits/annuli_data.csv",'w+')
    file_to_write.write("R_in,R_out,Temperature,Abundance,Density,Pressure,Entropy,T_Cool,AGN\n")
    file_min = open("Fits/annuli_data_min.csv",'w+')
    file_min.write("R_in,R_out,Temperature,Abundance,Density,Pressure,Entropy,T_Cool,AGN\n")
    file_max = open("Fits/annuli_data_max.csv",'w+')
    file_max.write("R_in,R_out,Temperature,Abundance,Density,Pressure,Entropy,T_Cool,AGN\n")
    #Go through each annuli
    for ann in annuli_data:
        ann.calc_all(redshift)
        ann.save_data(file_to_write,file_min,file_max)
    file_to_write.close()
    file_min.close()
    file_max.close()
    return None
