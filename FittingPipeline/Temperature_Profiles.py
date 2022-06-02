'''
Python Routine to wrap together Temperature Map Fitting given a binning scheme
What should you already have?
    - binning scheme (WVT perhaps)
    - blank sky background
    - Fits and Image file used for spectral extraction
'''
#-----------------------------------------------IMPORTS--------------------------------------------------#
import os
import sys
from read_input import read_input_file
from Fits import Fitting
from Fits_Deprojected import Fitting_Deprojected
from Plots import plot_data
from diffuse_specextract_blank import main_extract
from tqdm import tqdm
import numpy as np
#-----------------------------------------------READ IN--------------------------------------------------#
inputs = read_input_file(sys.argv[1])
base = inputs['base_dir']+inputs['Name']
num_bins = int(inputs['num_files'])
#----------------------------------------------------SPECTRA---------------------------------------------------#
if inputs['extract_spectrum'].lower() == 'true':
    for reg_file_ct in tqdm(np.arange(num_bins)):
        reg_file = inputs['reg_file_prefix']+str(reg_file_ct)
        # For each region extract the spectra in each ObsID
        main_extract(base, base+'/regions', inputs['ObsIDs'], reg_file)
#-----------------------------------------------FIT SPECTRA-------------------------------------------#
if inputs['fit_spec'].lower() == 'true':
    # Deprojection
    Fitting_Deprojected(inputs['base_dir']+'/'+inputs['Name'],inputs['ObsIDs'],inputs['reg_file_prefix'],int(num_bins),inputs['redshift'],inputs['n_H'],inputs['Temp_Guess'],inputs['Temp_data'],base+'/regions/', inputs['reg_file_prefix'], num_bins)
    # Not Deprojected
    Fitting(inputs['base_dir']+'/'+inputs['Name'],inputs['ObsIDs'],inputs['reg_file_prefix'],int(num_bins),inputs['redshift'],inputs['n_H'],inputs['Temp_Guess'],inputs['Temp_data'],base+'/regions/')
#-----------------------------------------------PLOT FITS-----------------------------------------------#
if inputs['plot'].lower() == 'true':
    plot_data(base+'/'+inputs['Temp_data'],base+'/regions/',inputs['reg_files'],base,'standard',inputs['redshift'])
    plot_data(base+'/'+inputs['Temp_data'].split('.')[0]+'_deproj.txt',base+'/regions/',inputs['reg_files'],base,'deproj',inputs['redshift'])
