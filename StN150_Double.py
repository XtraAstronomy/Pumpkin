'''
Python script that uses XSPEC to create synthetic ICM X-ray Spectra
'''

#--------------------------------IMPORTS---------------------------------------#
import numpy as np
import random
import os
from tqdm import tqdm
from sherpa.astro.ui import *
#-------------------------------VARIABLES--------------------------------------#
exp_time = 300  # Exposure Time in Seconds
num_spec = 1000
temp_min = 0.1
temp_max = 4
redshift = 0.018
n_H = 0.14
output_dir = '/your/path/here/StN150Double'
#-------------------------------FUNCTIONS--------------------------------------#
def temp_random_gen(temp_min,temp_max,num_spec):
    temp = []
    for i in range(num_spec):
        # Generate two random values
        ran_val1 = np.round(random.uniform(temp_min, temp_max),2)
        ran_val2 = np.round(random.uniform(temp_min, temp_max),2)
        temp.append([ran_val1,ran_val2])
    return temp


def create_synthetic_sherpa(num_spec,exp_time,temp1,temp2,redshift,n_H,metal,ct):
    '''
    Create synthetic data using Sherpa's fake_pha command
    This attaches poisson noise to the data
    '''
    # Read in Calibration arf and rmf files
    arf1 = unpack_arf("Chandra_acis/acisi_aimpt_cy21.arf")
    rmf1 = unpack_rmf("Chandra_acis/acisi_aimpt_cy21.rmf")
    #Set the source
    set_source("faked", xsphabs.abs1*(xsapec.apec1+xsapec.apec2))
    apec1.Redshift = redshift
    apec1.kT = temp1
    apec1.Abundanc = metal
    abs1.nH = n_H
    apec2.Redshift = redshift
    apec2.kT = temp2
    apec2.Abundanc = metal
    # Fake Spectra
    fake_pha("faked", arf1, rmf1, exposure=exp_time, grouped=False, backscal=1.0)
    # Save as fits file
    save_arrays(output_dir+'/'+'sim_data_multi_'+str(ct)+'.fits', [get_data_plot("faked").xlo, get_data_plot("faked").y], ascii=False)
    return None


temp = temp_random_gen(temp_min, temp_max, num_spec)
# os.chdir(output_dir)
# Clean out directory
for item in os.listdir(output_dir):
    if item.endswith(".fits"):
        os.remove(os.path.join(output_dir, item))
# Save model info to output file
with open(output_dir+'/'+'syn_data_inputs.txt', 'w+') as f_out:
    f_out.write('id temp1 temp2 redshift n_H \n')
    for i in tqdm(list(range(num_spec))):
        metal = np.random.uniform(0.2, 1.0)
        create_synthetic_sherpa(num_spec,exp_time,temp[i][0],temp[i][1],redshift,n_H,metal,i)
        f_out.write('%i %f %f %f %f %f\n'%(i, temp[i][0], temp[i][1], redshift, n_H, metal))
