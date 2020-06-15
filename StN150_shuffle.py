'''
Subroutine to take existing single and double thermal component spectra and shuffle
them in a new directory while tracking the spectral properties


'''
import os
import shutil
#------------------------INPUTS---------------------------#
base_dir = '/your/path/here'
spec_dirs = [base_dir+'StN150Single', base_dir+'StN150Double']
new_dir = '/your/path/hereStN150'
out_dir = '/your/path/here'

#----------------------FUNCTIONS--------------------------#
def relocate(spec_dirs,new_dir,out_dir):
    '''
    Take existing spectra and rename them in new directory. Also keep a file that
    tracks the details of each spectra.
    Must pass single then double spectra
    '''
    # Create tracking file
    track = open(out_dir+'/tracking_stn150.txt', 'w+')
    track.write('ID Temp1 Temp2 Temp3 Temp4 redshift n_H metal num_models \n')

    spec_ct = 0
    model_cts = 1
    for spec_dir in spec_dirs:
        # Open file contaiing info for each spec
        spec_info = open(spec_dir+'/syn_data_inputs.txt','r')
        next(spec_info)  # Skip the first line
        spec_info_ = []
        for line in spec_info:  # Get info in list of lists
            spec_info_.append([e.strip('\n') for e in line.split(' ')])
        # Step through each file in folder
        spec_ct_inner = 0  # spectra in specific directory
        for file in os.listdir(spec_dir):
            if file.endswith('.fits'):
                spec_ = spec_info_[spec_ct_inner]  # Spectral info
                # Copy spectra into new folder with new name
                shutil.copy(spec_dir+'/'+file,new_dir+'/spec_'+str(spec_ct)+'.fits')
                # Copy spectral info to new tracking file
                if model_cts == 1:  # Set temp2 == 0
                    track.write('%i %s %f %s %s %s %s %s %s\n'%(spec_ct,spec_[1], 0, 0,0, spec_[2], spec_[3], spec_[4], 'single'))
                elif model_cts ==2:
                    track.write('%i %s %s %s %s %s %s %s %s\n'%(spec_ct,spec_[1], spec_[2], 0, 0, spec_[3], spec_[4], spec_[5], 'double'))
                elif model_cts ==3:
                    track.write('%i %s %s %s %s %s %s %s %s\n'%(spec_ct,spec_[1], spec_[2], spec_[3],0,  spec_[4], spec_[5], spec_[6], 'triple'))
                elif model_cts ==4:
                    track.write('%i %s %s %s %s %s %s %s %s\n'%(spec_ct,spec_[1], spec_[2], spec_[3], spec_[4], spec_[5], spec_[6], spec_[7], 'quad'))
                spec_ct_inner += 1
                spec_ct += 1
        # Now multiple temperature profiles
        model_cts += 1

relocate(spec_dirs,new_dir,out_dir)
