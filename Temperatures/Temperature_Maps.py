'''
Python Routine to calculate temperature maps given:
    1 - A bin map of the cluster labelled by number of underlying thermal components
    2 - Extracted spectra for each bin region

'''
#-----------------------------------------------IMPORTS--------------------------------------------------#
import os
import sys
from read_input import read_input_file
from imagefits import create_image_fits
from Fits import Fitting
#-----------------------------------------------READ IN--------------------------------------------------#
inputs = read_input_file(sys.argv[1])
base = inputs['base_dir']+'/'+inputs['Name']
with open(base+'/'+inputs['component_map'], 'r') as f:
    next(f)
    num_bins = len(f.readlines())
#-----------------------------------------------FIT SPECTRA-------------------------------------------#
if inputs['fit_spec'].lower() == 'true':
    Fitting( inputs['base_dir']+'/'+inputs['Name'],inputs['ObsIDs'],inputs['source_file'],int(num_bins),
        inputs['redshift'],inputs['n_H'],inputs['Temp_Guess'],inputs['component_map'],inputs['output_dir'])
#-----------------------------------------------PLOT FITS-----------------------------------------------#
create_image_fits(inputs['base_dir'],inputs['image_fits'], os.getcwd(), inputs['WVT_data']+'.txt','/final_temperature_fits.csv')
