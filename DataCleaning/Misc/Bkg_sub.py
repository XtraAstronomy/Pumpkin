'''
Background Subtracted image from blank sky and other relevant functions

Functions:
    run_bkg_sub
    create_clean_img
    create_clean_image_merge
    exp_corr
'''
import os
from ciao_contrib.runtool import *

def run_bkg_sub(evt_file,image_file,obsid,filenames):
    '''
    Create a blanksy event file and then subtract from image fits to create a
    background subtracted image for annuli creation
    PARAMETERS:
        evt_file - name of event file for creation of Blanksky
        image_file - Name of image from which the background will be subtracted
        obsid - current observation
        filenames - list of filenames
    '''
    print("      Creating blanksky event file...")
    #Create Blanksky File
    blanksky.punlearn()
    blanksky.evtfile = evt_file
    blanksky.outfile = obsid+'_blank.evt'
    blanksky.tmpdir = './'
    blanksky.clobber = True
    blanksky()
    #Now create background subtracted image
    print("      Creating background-subtracted image")
    blanksky_image.punlearn()
    blanksky_image.bkgfile = obsid+'_blank.evt'
    blanksky_image.outroot = obsid+'_blank'
    blanksky_image.imgfile = image_file
    blanksky_image.tmpdir = './'
    blanksky_image.clobber = True
    blanksky_image()
    #Add to file names
    filenames['evt_bkgsub_img'] = os.getcwd()+'/'+obsid+'_blank_particle_bkgsub.img'
    return None

def create_clean_img(filenames):
    '''
    Create a clean image by removing any pt sources from the extended emission
    PARAMETERS:
        filenames - dictionary of files
    '''
    if sum(1 for line in open('pt_srcs.reg')) < 3: #Dont actually clean b/c no pt sources
        dmcopy.punlearn()
        dmcopy.infile = filenames['evt2_repro']
        dmcopy.outfile = filenames['evt2_repro'].split('.')[0] + '_uncontam.fits'
        dmcopy.clobber = True
        dmcopy()
    else: #Here we need to exclude the pt srcs
        dmcopy.punlearn()
        dmcopy.infile = filenames['evt2_repro']+'[exclude sky=region(pt_srcs.reg)]'
        dmcopy.outfile = filenames['evt2_repro'].split('.')[0]+'_uncontam.fits'
        dmcopy.clobber = True
        dmcopy()
    #Update uncontaminated filename
    filenames['evt2_repro_uncontam'] = filenames['evt2_repro'].split('.')[0]+'_uncontam.fits'
    #Create uncontaminated image
    dmcopy.punlearn()
    dmcopy.infile = filenames['evt2_repro_uncontam']
    dmcopy.outfile = 'evt_uncontam.img'
    dmcopy.opt = 'image'
    dmcopy.clobber = True
    dmcopy()
    #update uncontaminated image
    filenames['evt_uncontam_img'] = os.getcwd()+'/'+'evt_uncontam.img'
    return None

def create_clean_img_merge(filenames):
    '''
    Create clean merged image
    PARAMETERS:
        filenames - dictionary of files
    '''
    dmcopy.punlearn()
    dmcopy.infile = filenames['evt2_repro']
    dmcopy.outfile = filenames['evt2_repro'].split('.')[0] + '_uncontam.fits'
    dmcopy.clobber = True
    dmcopy()
    #Update uncontaminated filename
    filenames['evt2_repro_uncontam'] = filenames['evt2_repro'].split('.')[0] + '_uncontam.fits'
    #Create uncontaminated image
    dmcopy.punlearn()
    dmcopy.infile = filenames['evt2_repro_uncontam']
    dmcopy.outfile = 'evt_uncontam.img'
    dmcopy.opt = 'image'
    dmcopy.clobber = True
    dmcopy()
    #update uncontaminated image
    filenames['evt_uncontam_img'] = 'evt_uncontam.img'
    return None


def exp_corr(filenames):
    '''
    Create exposure corrected image after background subtraction
    *** NOT CURRENTLY WORKING ***
    PARAMETERS:
        filenames - directory of files
    '''
    fluximage.punlearn()
    fluximage.infile = filenames['evt_bkgsub_img']
    fluximage.outroot = 'flux/'
    fluximage.clobber = True
    fluximage()
    filenames['evt_bkgsub_img'] = os.getcwd()+'/flux/broad_flux.img'
    return None
