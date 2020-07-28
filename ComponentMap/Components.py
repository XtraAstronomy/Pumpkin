"""
Python routine to calculate the number of underlying bins given a WVT map and extracted spectra
This assumes you have the following pretrained algorithms in your directory:
    1 - ML_pred_StN150.class
    2 - PCA_StN150.class
Run this from the Pumpkin directory as python ComponentMap/Components.py ComponentMap/Perseus.i
"""
#-----------------------------------------------IMPORTS--------------------------------------------------#
import os
import sys
import pickle
from read_input import read_input_file
from CalculateComponents import calc_comps
from imagefits import create_image_fits
#-----------------------------------------------READ IN--------------------------------------------------#
inputs = read_input_file(sys.argv[1])
#-----------------------------------------------APPLY ALGO-----------------------------------------------#
# Read in classifier and PCA -- they should be in the Pumpkin directory
with open('ML_pred_StN150.class', 'rb') as f:
    classifier = pickle.load(f)
with open('PCA_StN150.class', 'rb') as f:
    pca = pickle.load(f)
# Calculate the number of regions
region_file = inputs['base_dir']+'/'+inputs['WVT_data']+'_bins.txt'
with open(region_file, 'r') as f:
    next(f); next(f)
    num_bins = len(f.readlines())
# Calculate the number of underlying components in each bin
calc_comps(inputs['base_dir'], inputs['ObsIDs'], inputs['source_file'], inputs['output_dir'], classifier, pca, num_bins)
# Create fits image
create_image_fits(inputs['base_dir'],inputs['image_fits'], os.getcwd(), inputs['WVT_data']+'.txt','/final_classification.txt')
