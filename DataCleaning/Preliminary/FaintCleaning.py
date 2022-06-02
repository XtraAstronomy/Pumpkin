'''
This python script contains a full reprocessing suite to clean especially faint and extended X-ray observations

INPUTS:
chandra_dir -- path to chandra directory (i.e. '/home/usr/Documents/Data')
OBSID -- OBSID of interest (i.e. '#####')
source -- region file containing source -- only used for astrometric corrections (i.e. 'source.reg')
source_ra -- right ascension of source (i.e. '##:##:##.#')
source_dec -- declination of source (i.e. '##:##:##.#')
output_dir -- name of output directory (i.e. 'repro')
flare_gti -- gti file created from background flare cleaning (i.e. 'ccd2_bkg_clean.gti')

NOTES:
If running the Flares module assumes that we have already created a background light Curve
	and create a gti file from it in the primary directory

'''

import os
from shutil import copyfile
from ciao_contrib.runtool import *
import matplotlib.pyplot as plt
from Preliminary.Astrometric import Astrometric
from Preliminary.Destreak import Destreak
from Preliminary.BadPixel import BadPixel
from Preliminary.Flares import Flares
from Preliminary.Process import Process
from Misc.filenames import get_filenames
#----------------INPUTS-------------------#
output_dir = 'repro'
#-----------------------------------------#


def FaintCleaning(chandra_dir,OBSID,ccd_bkg,source_ra,source_dec,ccds):
	'''
	Reprocess data for a faint and diffuse object
	PARAMETERS:
		chandra_dir - path to chandra directory
		OBSID - OBSID of interest
		ccd_bkg - number of background ccd
		source_ra - right ascension of source
		source_dec - declination of source
		ccds - list of all ccd numbers
	'''
	base_dir = chandra_dir+'/'+OBSID
	os.chdir(base_dir)
	filenames,biases = get_filenames()
	#print(filenames)
	if not os.path.exists(os.getcwd()+'/'+output_dir):
		os.makedirs(os.getcwd()+'/'+output_dir)
	os.chdir(base_dir+'/'+output_dir)
	#print("Appling Astrometric Corrections...")
	#Astrometric(OBSID,filenames,source_ra,source_dec)
	print("      Appling Background Flare Information...")
	os.chdir(base_dir)
	Flares(ccd_bkg+'_bkg_clean.gti',base_dir,output_dir,filenames)
	os.chdir(base_dir+'/'+output_dir)
	print("      Destreaking Event File...")
	Destreak(base_dir,output_dir,filenames)
	print("      Creating New Badpixel File...")
	BadPixel(base_dir,output_dir,OBSID,filenames,biases)
	print("      Apply GTI and Completing Reprocessing...")
	filenames = Process(filenames,OBSID)
	plt.close()
	return filenames
