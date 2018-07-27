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

#MAX table
MAX = ascii.read('/lustre/aoc/students/jotter/tables/MAX.txt')
MAX['RA_MAX'] = RA_to_deg(MAX['RAh'], MAX['RAm'], MAX['RAs'])
MAX['DEd'][np.where(MAX['DE-'] == '-')] *= -1
MAX['DEC_MAX'] = DEC_to_deg(MAX['DEd'], MAX['DEm'], MAX['DEs'])
MAX.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
MAX.rename_column('HC2000-Seq', 'HC_ID')
MAX['HC_ID'] = MAX['HC_ID'].filled(-1).astype(int)
data = join(data, MAX, keys='HC_ID', join_type='left')

#MRD2012 data
MRD = ascii.read('/lustre/aoc/students/jotter/tables/MRD2012(2).txt')
MRD['RA_MRD'] = RA_to_deg(MRD['RAh'], MRD['RAm'], MRD['RAs'])
MRD['DEd'][np.where(MRD['DE-'] == '-')] *= -1
MRD['DEC_MRD'] = DEC_to_deg(MRD['DEd'], MRD['DEm'], MRD['DEs'])
MRD.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
MRD['D_ID'] = np.full(len(MRD), -1)

MRD_coord = SkyCoord(MRD['RA_MRD'].quantity.value*u.degree, MRD['DEC_MRD'].quantity.value*u.degree)
HC_coord = SkyCoord(data['RA_HC']*u.degree, data['DEC_HC']*u.degree)
idx, d2d, d3d = MRD_coord.match_to_catalog_sky(HC_coord)
match = np.where(d2d.degree < (1/3600)) #matches are within 1 arcsec

for all_ind in match[0]:
	MRD[all_ind]['D_ID'] = data[idx[all_ind]]['D_ID']

data = join(data, MRD, keys='D_ID', join_type='left')

#OW94 table
OW94 = ascii.read('/lustre/aoc/students/jotter/tables/OW94.txt', data_start=7, data_end=387, header_start=4)
OW94['RA_OW94'] = RA_to_deg(OW94['RAh'], OW94['RAm'], OW94['RAs'])
OW94['DEC_OW94'] = DEC_to_deg(OW94['DEd'], OW94['DEm'], OW94['DEs'])
OW94.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
OW94['D_ID'] = np.full(len(OW94), -1)

OW_coord = SkyCoord(OW94['RA_OW94']*u.degree, OW94['DEC_OW94']*u.degree)
HC_coord = SkyCoord(data['RA_HC']*u.degree, data['DEC_HC']*u.degree)

idx, d2d, d3d = OW_coord.match_to_catalog_sky(HC_coord)
#idx is a list of indices for data with the list index corresponding to the match in data
match = np.where(d2d.degree < 2*(1/3600)) #matches are within 1 arcsec

for all_ind in match[0]:
	OW94[all_ind]['D_ID'] = data[idx[all_ind]]['D_ID']

data = join(data, OW94, keys='D_ID', join_type='left')

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

ind = np.where(data['_idx_B3'] == 94)
ind_ref = np.where(data['_idx_B3'] == 97) #ref sources:0(bad),8(bad),7(kinda bad),82(okay),97(ok)

HC_xerr = 0.017/(60*60) #from the paper
HC_yerr = 0.028/(60*60)
COUP_poserr = data['PosErr_COUP'][ind].quantity.value[0]/3600
MRD_poserr = 0.1/3600 #can't find actual error, conservative estimate
OW_poserr = 0.1/3600 #can't find actual error, conservative estimate
if data['PosFlag'][ind] == 0:
	MAX_poserr = 0.1/3600
else:
	MAX_poserr = 0.2/3600
MLLA_poserr = 0.1/(60*60) #MLLA error about 0.1"
RRS_poserr = 0.025/3600 #25mas, mentioned in paper but not certain

RAs = [float(data['RA_COUP'][ind] - data['RA_COUP'][ind_ref]),float(data['RA_HC'][ind] - data['RA_HC'][ind_ref]),float(data['gauss_x_B3'][ind] - data['gauss_x_B3'][ind_ref]),float(data['RA_MRD'][ind] - data['RA_MLLA'][ind_ref]),float(data['RA_OW94'][ind] - data['RA_OW94'][ind_ref]),float(data['RA_MAX'][ind] - data['RA_MAX'][ind_ref]),float(data['RA_MLLA'][ind] - data['RA_MRD'][ind_ref]),float(data['RA_RRS'][ind] - data['RA_RRS'][ind_ref])]
DECs = [float(data['DEC_COUP'][ind] - data['DEC_COUP'][ind_ref]),float(data['DEC_HC'][ind] - data['DEC_HC'][ind_ref]),float(data['gauss_y_B3'][ind] - data['gauss_y_B3'][ind_ref]),float(data['DEC_MLLA'][ind] - data['DEC_MLLA'][ind_ref]),float(data['DEC_OW94'][ind] - data['DEC_OW94'][ind_ref]),float(data['DEC_MAX'][ind] - data['DEC_MAX'][ind_ref]),float(data['DEC_MRD'][ind] - data['DEC_MRD'][ind_ref]),float(data['DEC_RRS'][ind] - data['DEC_RRS'][ind_ref])]
RA_err = [COUP_poserr,HC_xerr,data['x_err_B3'][ind],MLLA_poserr,OW_poserr,MAX_poserr,MRD_poserr,RRS_poserr]
DEC_err = [COUP_poserr,HC_yerr,data['y_err_B3'][ind],MLLA_poserr,OW_poserr,MAX_poserr,MRD_poserr,RRS_poserr]

COUP_date = (1,2003)
COUP_err = 0.5/12
HC_date = (10,1999)
HC_err = 0.5/12
B3_date = (10,2017)
B3_err = 0.5/12
MLLA_date, MLLA_err = middle_date(12,1997,3,2000)
OW94_date = (1,1994)
OW94_err = 0.5/12
MAX_date, MAX_err = middle_date(11,1998,12,2000)
MRD_date, MRD_err = middle_date(10,2004,4,2005)
RRS_date, RRS_err = middle_date(11,2004,4,2005)

dates = [COUP_date,HC_date,B3_date,MLLA_date,OW94_date,MAX_date,MRD_date,RRS_date]
times = calc_times(dates)

times_err = [COUP_err,HC_err,B3_err,MLLA_err,OW94_err,MAX_err,MRD_err,RRS_err]

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
