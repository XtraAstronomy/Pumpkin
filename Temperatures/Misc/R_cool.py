'''
Calculate Cooling Radius defined at 3 Gyr for Non AGN fits
'''
import numpy as np
#import pandas as pd
from scipy import interpolate
from Misc.LSCalc import ls_calc
from Database.Add_new import add_r_cool

import matplotlib.pyplot as plt

def int_rcool(regions,data,val_to_find):
    yToFind = val_to_find
    yreduced = np.array(data) - yToFind
    freduced = interpolate.UnivariateSpline(regions, yreduced)
    if len(freduced.roots()) > 0:
        val = freduced.roots()[-1]
    else:
        val = 0
    return val

def R_cool_calc(mydb,mycursor,cluster_id,cluster_name,data_folder,redshift,main_out):
    sql_select_Query = "select T_cool,T_cool_min,T_cool_max,AGN,R_in,R_out from Region WHERE idCluster=%s ORDER BY idRegion"%(cluster_id)
    mycursor.execute(sql_select_Query)
    records = mycursor.fetchall()
    data = []; data_min = []; data_max = []; agn_ = []; r_in = []; r_out = [];
    for row in records:
        if row[0] != None:
            data.append(float(row[0]))
            data_min.append(float(row[1]))
            data_max.append(float(row[2]))
            agn_.append(row[3])
            r_in.append(row[4])
            r_out.append(row[5])
    regions = []
    NonAGN_data = [];
    NonAGN_min = [];
    NonAGN_max = [];
    #arcsec_to_kpc = ls_calc(redshift,1)#arcsec to kpc conversion factor
    for region in range(len(r_in)):
        if agn_[region] == 0: #no agn
            inner = r_in[region]
            outer = r_out[region]
            mid_point = (inner+outer)/2
            regions.append(mid_point)#*arcsec_to_kpc)
            NonAGN_data.append(data[region])
            NonAGN_min.append(data_min[region])
            NonAGN_max.append(data_max[region])

    try:
        R_cool_3 = int_rcool(regions,NonAGN_data,3)
        R_cool_3_l = int_rcool(regions,NonAGN_max,3)
    except:
        R_cool_3 = 0
        R_cool_3_l = 0
    try:
        R_cool_3_u = int_rcool(regions,NonAGN_min,3)
    except:
        R_cool_3_u = 0
    try:
        R_cool_7 = int_rcool(regions,NonAGN_data,7.7)
        R_cool_7_l = int_rcool(regions,NonAGN_max,7.7)
    except:
        R_cool_7 = 0
        R_cool_7_l = 0
    try:
        R_cool_7_u = int_rcool(regions,NonAGN_min,7.7)
    except:
        R_cool_7_u = 0
    main_out.write("The Cooling Radius at 3 Gyr is %.2fkpc\n"%R_cool_3)
    main_out.write("We are unable to calculate the 7.7 Gyr Cooling Radius.")
    add_r_cool(mydb,mycursor,cluster_id,cluster_name,R_cool_3,R_cool_3_l,R_cool_3_u,R_cool_7,R_cool_7_l,R_cool_7_u)

    return None
