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
from binned_spectra import create_spectra
from WVT import wvt_main
#-----------------------------------------------READ IN--------------------------------------------------#
inputs = read_input_file(sys.argv[1])
base = inputs['base_dir']+'/'+inputs['Name']
#----------------------------------------------------WVT---------------------------------------------------#
if inputs['wvt'].lower() == 'true':
    wvt_main(inputs,base,inputs['WVT_data'])
#-----------------------------------------------BIN SPECTRA-------------------------------------------#
num_bins = 0
if inputs['bin_spec'].lower() == 'true':
    num_bins = create_spectra(inputs['base_dir']+'/'+inputs['Name'],inputs['WVT_data'],inputs['ObsIDs'],inputs['source_file'],inputs['output_dir'],inputs['WVT_data'])
if inputs['bin_spec'].lower() == 'false':
    print("You need to change the 'bin_spec' argument in Perseus.i to True!")
