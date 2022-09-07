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
redshift = 0.01
n_H = 0.01
output_dir = '/your/path/here/StN150Single'
#-------------------------------FUNCTIONS--------------------------------------#

def temp_random_gen(temp_min,temp_max,num_spec):
    temp = []
    for i in range(num_spec):
        ran_val = np.round(random.uniform(temp_min, temp_max),1)
        temp.append(ran_val)
    return temp


def create_synthetic_sherpa(num_spec,exp_time,temp,redshift,n_H,metal,ct):
    '''
    Create synthetic data using Sherpa's fake_pha command
    This attaches poisson noise to the data
    '''
    # Read in Calibration arf and rmf files
    arf1=unpack_arf("Chandra_acis/acisi_aimpt_cy21.arf")
    rmf1=unpack_rmf("Chandra_acis/acisi_aimpt_cy21.rmf")
    #Set the source
    set_source("faked", xsphabs.abs1*xsapec.apec)
    apec.Redshift = redshift
    apec.kT = temp
    apec.Abundanc = metal
    abs1.nH = n_H
    # Fake Spectra
    fake_pha("faked", arf1, rmf1, exposure=exp_time, grouped=False, backscal=1.0)
    # Save as fits file
    save_arrays(output_dir+'/'+'sim_data_'+str(ct)+'.fits', [get_data_plot("faked").xlo, get_data_plot("faked").y], ascii=False)
    return None


temp = temp_random_gen(temp_min, temp_max, num_spec)
# os.chdir(output_dir)
# Clean out directory
for item in os.listdir(output_dir):
    if item.endswith(".fits"):
        os.remove(os.path.join(output_dir, item))
# Save model info to output file
with open(output_dir+'/'+'syn_data_inputs.txt', 'w+') as f_out:
    f_out.write('id temp redshift n_H \n')
    for i in tqdm(list(range(num_spec))):
        metal = np.random.uniform(0.2, 1.0)
        create_synthetic_sherpa(num_spec,exp_time,temp[i],redshift,n_H,metal,i)
        f_out.write('%i %f %f %f %f\n'%(i, temp[i], redshift, n_H, metal))
