'''
Small script to merge objects

We are merging the background subtracted images in each obsid because we don't use the newly created evt file since
we only want the image for calculating the centroid, extent of emission, and annuli :)

'''
import os
from ciao_contrib.runtool import *


def merge_objects(Obsids,output_name,clean='yes'):
    '''
    Merge background subtracted event files for photometric analysis
    PARAMETERS:
        Obsids - list of observation ids to merge
        output_name - name of output directory
        clean - clean up temporary files (default 'yes')
    '''
    id_string = ''
    id_hyphen = ''
    for obsid in Obsids:
        id_string += obsid+"/repro/acisf"+obsid+"_repro_evt2_uncontam.fits,"
        id_hyphen += obsid+"-"
    os.system("merge_obs '"+id_string+"' "+output_name+"_Soft/ clobber=yes binsize=1 verbose=0 bands='0.5:2.0:1.32' cleanup="+clean )
    return None
