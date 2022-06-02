'''
Apply Astrometric Corrections to evt file
'''
from ciao_contrib.runtool import *
def Astrometric(OBSID,filenames,source_ra,source_dec):
    '''
    Apply astrometric corrections to event file
    PARAMETERS:
        OBSID - Chandra observation ID
        filenames - dictionary of import files for obsid
        source_ra - ra of x-ray centroid
        source_dec - dec of x_ray centroid
    '''
    #Create centered region
    with open('temp_src.reg','w+') as temp_src:
        temp_src.write("# Region file format: DS9 version 4.1 \n")
        temp_src.write("physical \n")
        temp_src.write('circle(%s,%s,1) \n'%(source_ra,source_dec))
    #Get location
    dmstat.punlearn()
    dmstat.infile = filenames['evt2']+'[sky=region(temp_src.reg)][bin x=::1,y=::1]'
    dmstat()
    cntrd_phys = dmstat.out_cntrd_phys.split(',')
    phys_x_obs = float(cntrd_phys[0])
    phys_y_obs = float(cntrd_phys[1])
    #Calculate physical coordinates for actual location
    dmcoords.punlearn()
    dmcoords.infile = filenames['evt2']#OBSID+'_broad_thresh.img'
    dmcoords.option = 'cel'
    dmcoords.celfmt = 'hms'
    dmcoords.ra = source_ra
    dmcoords.dec = source_dec
    dmcoords()
    phys_x_ref = dmcoords.x
    phys_y_ref = dmcoords.y
    diff_x = phys_x_ref-phys_x_obs
    diff_y = phys_y_ref-phys_y_obs
    #Make copies of event file and asol file
    dmcopy.punlearn()
    dmcopy.infile = filenames['evt2']
    dmcopy.outfile = filenames['evt2']+'.corrected'
    dmcopy.clobber = True
    dmcopy()
    dmcopy.punlearn()
    dmcopy.infile = filenames['asol1']
    dmcopy.outfile = filenames['asol1']+'.corrected'
    dmcopy.clobber = True
    dmcopy()
    #Correct event file and asol file
    wcs_update.punlearn()
    wcs_update.infile = filenames['evt2']+'.corrected'
    wcs_update.outfile = ''
    wcs_update.wcsfile = filenames['evt2']
    wcs_update.deltax = diff_x
    wcs_update.deltay = diff_y
    wcs_update.clobber = True
    wcs_update()
    wcs_update.punlearn()
    wcs_update.infile = filenames['asol1']+'.corrected'
    wcs_update.outfile = 'acisf'+OBSID+'_new_asol.fits'
    wcs_update.wcsfile = OBSID+'_broad_thresh.img'
    wcs_update.deltax = diff_x
    wcs_update.deltay = diff_y
    wcs_update.clobber = True
    wcs_update()
    return None
