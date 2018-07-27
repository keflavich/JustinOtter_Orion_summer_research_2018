#SIMBAD name: [SCE2006] 15

import matplotlib.pyplot as plt
from astropy.io import fits, ascii
from astropy.table import Table, join
import numpy as np
import astropy.units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, Angle
from PM_fit import calc_pm
from calc_dates import *

data = Table(fits.getdata('/lustre/aoc/students/jotter/dendro_catalogs/IR_matched_catalog.fits')) 

#MLLA table
MLLA = ascii.read('/lustre/aoc/students/jotter/tables/MLLA.txt')
MLLA['RA_MLLA'] = RA_to_deg(MLLA['RAh'], MLLA['RAm'], MLLA['RAs'])
MLLA['DEd'][np.where(MLLA['DE-'] == '-')] *= -1
MLLA['DEC_MLLA'] = DEC_to_deg(MLLA['DEd'], MLLA['DEm'], MLLA['DEs'])
MLLA.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
MLLA.rename_column('HC2000-Seq', 'HC_ID')
MLLA['HC_ID'] = MLLA['HC_ID'].filled(-1).astype(int)
data = join(data, MLLA, keys='HC_ID', join_type='left')

#COUP data
COUP = ascii.read('/lustre/aoc/students/jotter/tables/COUP.txt')
COUP.rename_column('RAdeg', 'RA_COUP')
COUP.rename_column('DEdeg', 'DEC_COUP')
COUP.rename_column('PosErr', 'PosErr_COUP')
COUP['D_ID'] = np.full(len(COUP), -1)
COUP_coord = SkyCoord(COUP['RA_COUP'], COUP['DEC_COUP'])
HC_coord = SkyCoord(data['RA_HC']*u.degree, data['DEC_HC']*u.degree)

idx, d2d, d3d = COUP_coord.match_to_catalog_sky(HC_coord)
#idx is a list of indices for data with the list index corresponding to the match in data
match = np.where(d2d.degree < (1/3600)) #matches are within 1 arcsec

for all_ind in match[0]:
	COUP[all_ind]['D_ID'] = data[idx[all_ind]]['D_ID']

data = join(data, COUP, keys='D_ID', join_type='left')

#FDM table
FDM = ascii.read('/lustre/aoc/students/jotter/tables/FDM2003.txt')
FDM['RA_FDM'] = RA_to_deg(FDM['RAh'], FDM['RAm'], FDM['RAs'])
FDM['DEd'][np.where(FDM['DE-'] == '-')] *= -1
FDM['DEC_FDM'] = DEC_to_deg(FDM['DEd'], FDM['DEm'], FDM['DEs'])
FDM.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
FDM['D_ID'] = np.full(len(FDM), -1)
FDM.rename_column('PosErr', 'PosErr_FDM')

FDM_coord = SkyCoord(FDM['RA_FDM'].quantity.value*u.degree, FDM['DEC_FDM'].quantity.value*u.degree)
HC_coord = SkyCoord(data['RA_HC']*u.degree, data['DEC_HC']*u.degree)

idx, d2d, d3d = FDM_coord.match_to_catalog_sky(HC_coord)
#idx is a list of indices for data with the list index corresponding to the match in data
match = np.where(d2d.degree < (1/3600)) #matches are within 1 arcsec

for all_ind in match[0]:
	FDM[all_ind]['D_ID'] = data[idx[all_ind]]['D_ID']

data = join(data, FDM, keys='D_ID', join_type='left')


ind62 = np.where(data['_idx_B3'] == 62)
ind_ref = np.where(data['_idx_B3'] == 3) #ref sources: 32(meh),82(bad),94(good),0(bad),1(meh),3(ok)

HC_xerr = 0.017/(60*60) #from the paper
HC_yerr = 0.028/(60*60)

COUP_poserr = data['PosErr_COUP'][ind62].quantity.value[0]/3600
FDM_poserr = data['PosErr_FDM'][ind62].quantity.value[0]/3600

MLLA_poserr = 0.1/(60*60) #MLLA error about 0.1"

RAs = [float(data['RA_COUP'][ind62] - data['RA_COUP'][ind_ref]),float(data['RA_HC'][ind62] - data['RA_HC'][ind_ref]),float(data['gauss_x_B3'][ind62] - data['gauss_x_B3'][ind_ref]),float(data['RA_FDM'][ind62] - data['RA_FDM'][ind_ref]),float(data['RA_MLLA'][ind62] - data['RA_MLLA'][ind_ref])]
DECs = [float(data['DEC_COUP'][ind62] - data['DEC_COUP'][ind_ref]),float(data['DEC_HC'][ind62] - data['DEC_HC'][ind_ref]),float(data['gauss_y_B3'][ind62] - data['gauss_y_B3'][ind_ref]),float(data['DEC_FDM'][ind62] - data['DEC_FDM'][ind_ref]),float(data['DEC_MLLA'][ind62] - data['DEC_MLLA'][ind_ref])]
RA_err = [COUP_poserr,HC_xerr,data['x_err_B3'][ind62],FDM_poserr, MLLA_poserr]
DEC_err = [COUP_poserr,HC_yerr,data['y_err_B3'][ind62],FDM_poserr, MLLA_poserr]

COUP_date = (1,2003)
COUP_err = 0.5/12
HC_date = (10,1999)
HC_err = 0.5/12
B3_date = (10,2017)
B3_err = 0.5/12
FDM_date = (2,2000)
FDM_err = 0.5/12
MLLA_date, MLLA_err = middle_date(12,1997,3,2000)

dates = [COUP_date,HC_date,B3_date,FDM_date,MLLA_date]
times = calc_times(dates)

times_err = [COUP_err,HC_err,B3_err,FDM_err,MLLA_err]

v = calc_pm(RAs, DECs, RA_err, DEC_err, times, times_err)
plt.show()
'''
#B3 ID 20
fig3 = plt.figure()
FW2011 = [5,35,14.656,-5,22,38.36]
names=['FW2011', 'HC2000', 'B3']
RAs = [RA_to_deg(FW2011[0],FW2011[1],FW2011[2]),data['RA_HC'][1],data['gauss_x_B3'][1]]
DECs = [DEC_to_deg(FW2011[3],FW2011[4],FW2011[5]),data['DEC_HC'][1],data['gauss_y_B3'][1]]
x_err = [0,0,data['x_err_B3'][1]]
y_err = [0,0,data['y_err_B3'][1]]

plt.errorbar(RAs[2], DECs[2], xerr=x_err[2], yerr=y_err[2], label=names[2])
plt.scatter(RAs[0], DECs[0], label=names[0])
plt.scatter(RAs[1], DECs[1], label=names[1])
plt.legend()'''
