'''
Small script to collect all relavent file names
'''
import os
def get_filenames():
    '''
    Collect all relevant files for reduction/analysis and place into a dictionary
    '''
    filenames = dict()
    biases = []
    for file in os.listdir(os.getcwd()+'/primary'):
        if file.endswith("_evt2.fits"):
            filenames['evt2'] = os.getcwd()+'/primary/'+ file
        if file.endswith("_asol1.fits"):
            filenames['asol1'] = os.getcwd()+'/primary/'+ file
    for file in os.listdir(os.getcwd()+'/secondary'):
        if file.endswith("_msk1.fits"):
            filenames['msk1'] = os.getcwd()+'/secondary/'+ file
        if file.endswith("_stat1.fits"):
            filenames['stat1'] = os.getcwd()+'/secondary/'+ file
        if file.endswith("_pbk0.fits"):
            filenames['pbk0'] = os.getcwd()+'/secondary/'+ file
        if file.endswith("_evt1.fits"):
            filenames['evt1'] = os.getcwd()+'/secondary/'+ file
        if file.endswith("_mtl1.fits"):
            filenames['mtl1'] = os.getcwd()+'/secondary/'+ file
        if file.endswith("_flt1.fits"):
            filenames['flt1'] = os.getcwd()+'/secondary/'+ file
        if file.endswith("_bias0.fits"):
            bias_number = file.split("_")[1]
            filenames[bias_number+'_bias0'] = os.getcwd()+'/secondary/'+ file
            biases.append(bias_number)
    return filenames,biases
