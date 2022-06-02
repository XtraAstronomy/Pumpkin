'''
PIPELINE FOR CLEANING CHANDRA DATA:

For suggestions/comments/errata please contact:
Carter Rhea
carter.rhea@umontreal.ca
'''
#------------------------------------IMPORTS-----------------------------------#
#----------------------------------GENERAL IMPORTS-----------------------------#
import os
import sys
import shutil
import easygui as gui
from shutil import copyfile
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from ciao_contrib.runtool import *

#-------------------------------Additional IMPORTS----------------------------#
from Misc.read_input import read_input_file
from Misc.Bkg_sub import run_bkg_sub, create_clean_img, exp_corr, create_clean_img_merge
from Preliminary.unzip import unzip
from Preliminary.Merge import merge_objects
from Preliminary.CCD_split import split_ccds
from Preliminary.FaintCleaning import FaintCleaning
from Preliminary.CreateLightcurves import bkg_clean_srcs, bkg_lightcurve
from Preliminary.chips_ccd import AGN,display_ccds, display_entire, display_merge
#------------------------------------------------------------------------------#
#------------------------------------PROGRAM-----------------------------------#
def run_pipeline():
    #---------------------------Read in data----------------------------------#
    print("Reading Input File and Running Preliminary Steps...")
    inputs,merge_bool = read_input_file(sys.argv[1])
    print("#-------STARTING ANALYSIS ON %s-------#"%inputs['name'])
    #inputs,merge_bool = read_input_file(input_file)
    os.chdir(inputs['home_dir'])
    #Unzip all relavent files
    unzip(inputs['home_dir'],inputs['dir_list'])
    print("Generating fits and image files for each individual CCD...")
    ccds = split_ccds(inputs['home_dir'],inputs['dir_list'])
    if not os.path.exists(inputs['home_dir']+'/'+inputs['name']):
        os.makedirs(inputs['home_dir']+'/'+inputs['name'])
    main_out = open(inputs['home_dir']+'/'+inputs['name'] + "/Additional.txt", 'w+')
    #--------------------------------Multiple Obsid Scenario--------------------------------------#
    print("#-----Multiple Observation Mode----#")
    #We must clean each observation first :)
    print("Beginning cleaning process for each individual obsid...")
    for obsid_ in inputs['dir_list']: #left as a list to keep input deck the same and sample :)
        if inputs['cleaning'].lower() == 'true':
            main_out_obsid = open(inputs['home_dir'] + "/" + obsid_ + "/decisions.txt", 'w+')
            os.chdir(inputs['home_dir'] + '/' + obsid_ + '/Background')
            print("We are on obsid %s"%obsid_)
            main_out_obsid.write('Obsid %s'%obsid_)
            print("    Now let us pick our background ccd...")
            #Lets take a look at each ccd and pick our background and src ccds
            bkg_ccd = display_ccds(ccds,obsid_,Merge=True)
            main_out_obsid.write("The background CCD chosen is CCD#%s\n"%bkg_ccd)
            print("    We can now create a lightcurve for the background...")
            bkg_clean_srcs(bkg_ccd)
            bkg_lightcurve(bkg_ccd,obsid_)
            print("    We need to clean our diffuse emission...")
            filenames = FaintCleaning(inputs['home_dir'],obsid_,bkg_ccd,0,0,ccds[obsid_])
            #We have to create bkg-subtracted images for each obsid because we need them for our merged image!
            os.chdir(inputs['home_dir'] + '/' + obsid_ + '/repro')
            print("    Creating Clean Image...")
            create_clean_img_merge(filenames)
            print("    Running Background Subtraction...")
            run_bkg_sub(filenames['evt2_repro_uncontam'], filenames['evt_uncontam_img'], obsid_, filenames)
            main_out_obsid.close()
    #os.chdir(inputs['home_dir']+'/'+inputs['dir_list'][0])
    #filenames,temp = get_filenames()
    #filenames['evt2_repro'] = inputs['home_dir']+'/'+inputs['name']+'/merged_evt.fits'
    #filenames['evt2_repro_uncontam'] = filenames['evt2_repro'].split('.')[0]+'_uncontam.fits'
    #filenames['evt_bkgsub_img'] = inputs['home_dir']+'/'+inputs['name']+'/broad_flux.img'
    #filenames['evt_uncontam_img'] = inputs['home_dir']+'/'+inputs['name']+'/broad_flux.img'
    print("Beginning Merged Calculations...")
    print("    Merging obsids...")
    os.chdir(inputs['home_dir'])
    merge_objects(inputs['dir_list'], inputs['name'], clean='yes')
    '''os.chdir(inputs['home_dir']+'/'+inputs['name'])
    filenames['evt2_repro'] = inputs['home_dir']+'/'+inputs['name']+'/merged_evt.fits'
    print("    Choosing extent of source and contaminating point sources")
    edge_ra,edge_dec,agn_ = display_merge(inputs['home_dir']+'/'+inputs['name'],'broad_flux.img')
    #edge_ra,edge_dec = get_RaDec_log('broad_flux.img',edge_x,edge_y)
    main_out.write('The edge point is chosen to be %s,%s \n' % (edge_ra, edge_dec))
    os.chdir(inputs['home_dir']+'/'+inputs['name'])
    print("    Calculating centroid position")
    cen_ra,cen_dec = merged_centroid('broad_flux.img')
    main_out.write('The center point is chosen to be %s,%s \n' % (cen_ra, cen_dec))
    filenames['exp_corr'] = inputs['home_dir']+'/'+inputs['name']+'/broad_flux.img' #Need this defined
    #Calculate additional needed parameters
    create_src_img(filenames['exp_corr'],[cen_ra,cen_dec],[edge_ra,edge_dec])
    main_out.close()'''
    return None
run_pipeline()
#main()
