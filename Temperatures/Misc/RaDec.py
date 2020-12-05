'''
Change to RA/DEC coordinate system from Physical units
'''
from ciao_contrib.runtool import dmcoords
#Get ra/dec
def get_RaDec(evt_file,cen_x,cen_y):
    dmcoords.punlearn()
    if evt_file.split('.')[-1] == 'img' or evt_file.split('.')[-1] == 'fits':
        dmcoords.infile = evt_file
    else:
        dmcoords.infile = evt_file+'.fits'  # OBSID+'_broad_thresh.img'
    dmcoords.option = 'sky'
    dmcoords.x = cen_x
    dmcoords.y = cen_y
    dmcoords()
    cen_ra = dmcoords.ra; cen_dec = dmcoords.dec
    return cen_ra,cen_dec

def get_RaDec_log(evt_file,cen_x,cen_y):
    dmcoords.punlearn()
    if evt_file.split('.')[-1] == 'img' or evt_file.split('.')[-1] == 'fits':
        dmcoords.infile = evt_file
    else:
        dmcoords.infile = evt_file+'.fits'  # OBSID+'_broad_thresh.img'
    dmcoords.option = 'logical'
    dmcoords.logicalx = cen_x
    dmcoords.logicaly = cen_y
    dmcoords()
    cen_ra = dmcoords.ra; cen_dec = dmcoords.dec
    return cen_ra,cen_dec
