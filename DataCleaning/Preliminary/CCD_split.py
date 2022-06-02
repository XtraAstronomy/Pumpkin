'''
Create ccd specific fits files for each CCD used
'''

import os
from ciao_contrib.runtool import *
from pycrates import *

#-----------------INPUTS------------------#
background_dir = 'Background'
#-----------------------------------------#

def split_ccds(chandra_dir,dir_to_split):
    '''
    Split CCDs and plot with appropriate labels
    PARAMETERS:
        chandra_dir - directory containing observations
        dir_to_split - list of OBSIDs 
    '''
    ccds_dict = {}
    for dir in dir_to_split:
        os.chdir(chandra_dir)
        print("    Working on obsid %s"%dir)
        #Basic Setup
        if not os.path.exists(dir+'/'+background_dir):
            os.makedirs(dir+'/'+background_dir)
        os.chdir(chandra_dir+'/'+dir+'/primary')
        evt2_file = None
        for file in os.listdir(os.getcwd()):
            #Get event file name
            if file.endswith("_evt2.fits"):
                evt2_file = os.getcwd() + '/'+ file
        evt_file_data = read_file(evt2_file)
        ccds = get_keyval(evt_file_data, 'DETNAM').split('-')[1]
        ccds = [i for i in ccds]
        ccds_dict[dir] = ccds
        os.chdir(chandra_dir+'/'+dir+'/'+background_dir)
        #Create fits files for each ccd
        for ccd in ccds:
            exists = os.path.isfile('ccd'+ccd+'.fits')
            if exists:
                print("        CCD%s event and image files already exist..."%ccd)
            else:
                print("        Creating event and image file for CCD%s"%ccd)
                dmcopy.punlearn()
                dmcopy.infile = evt2_file+'[ccd_id='+ccd+']'
                dmcopy.outfile = 'ccd'+ccd+'.fits'
                dmcopy.clobber = True
                dmcopy()
                dmcopy.punlearn()
                dmcopy.infile = evt2_file+'[ccd_id='+ccd+']'
                dmcopy.outfile = 'ccd'+ccd+'.img'
                dmcopy.option = 'image'
                dmcopy.clobber = True
                dmcopy()

        os.chdir(chandra_dir)
    return ccds_dict
