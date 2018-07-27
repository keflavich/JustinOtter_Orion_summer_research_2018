#SIMBAD name [FW2011] J053514.656-052238.363

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

#LML table
LML = ascii.read('/lustre/aoc/students/jotter/tables/LML2004.txt')
LML['RA_LML'] = RA_to_deg(LML['RAh'], LML['RAm'], LML['RAs'])
LML['DEd'][np.where(LML['DE-'] == '-')] *= -1
LML['DEC_LML'] = DEC_to_deg(LML['DEd'], LML['DEm'], LML['DEs'])
LML.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
LML.rename_column('HC2000-Seq', 'HC_ID')
LML['HC_ID'] = LML['HC_ID'].filled(-1).astype(int)
data = join(data, LML, keys='HC_ID', join_type='left')

#MLLA table
MLLA = ascii.read('/lustre/aoc/students/jotter/tables/MLLA.txt')
MLLA['RA_MLLA'] = RA_to_deg(MLLA['RAh'], MLLA['RAm'], MLLA['RAs'])
MLLA['DEd'][np.where(MLLA['DE-'] == '-')] *= -1
MLLA['DEC_MLLA'] = DEC_to_deg(MLLA['DEd'], MLLA['DEm'], MLLA['DEs'])
MLLA.remove_columns(('RAh', 'RAm', 'RAs', 'DEd', 'DEm', 'DEs'))
MLLA.rename_column('HC2000-Seq', 'HC_ID')
MLLA['HC_ID'] = MLLA['HC_ID'].filled(-1).astype(int)
data = join(data, MLLA, keys='HC_ID', join_type='left')

#FW2011 table
FW2011 = ascii.read('/lustre/aoc/students/jotter/tables/FW2011.txt', data_start=3, data_end=34, header_start=2)
RAh = np.array([int(st[0:2]) for st in FW2011['alpha_J2000']])
RAm = np.array([int(st[3:5]) for st in FW2011['alpha_J2000']])
RAs = np.array([float(st[6:12]) for st in FW2011['alpha_J2000']])
FW2011['RA_FW2011'] = RA_to_deg(RAh, RAm, RAs)
DEh = np.array([int(st[0:3]) for st in FW2011['delta_J2000']])
DEm = np.array([int(st[4:6]) for st in FW2011['delta_J2000']])
DEs = np.array([float(st[7:13]) for st in FW2011['delta_J2000']])
FW2011['DEC_FW2011'] = DEC_to_deg(DEh, DEm, DEs)
FW2011.remove_columns(('alpha_J2000', 'delta_J2000'))
FW2011['D_ID'] = np.full(len(FW2011), -1)

FW_coord = SkyCoord(FW2011['RA_FW2011']*u.degree, FW2011['DEC_FW2011']*u.degree)
B3_coord = SkyCoord(data['gauss_x_B3']*u.degree, data['gauss_y_B3']*u.degree)

 
idx, d2d, d3d = FW_coord.match_to_catalog_sky(B3_coord)
#idx is a list of indices for data with the list index corresponding to the match in data
match = np.where(d2d.degree < 0.5*(1/3600)) #matches are within 1 arcsec
for all_ind in match[0]:
	FW2011[all_ind]['D_ID'] = data[idx[all_ind]]['D_ID']
data = join(data, FW2011, keys='D_ID', join_type='left')

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

ind20 = np.where(data['_idx_B3'] == 20)
ind_ref = np.where(data['_idx_B3'] == 3) #ref sources: 9(kinda bad), 97(good), 0(eh), 1(bad), 2(bad), 3(good)

HC_xerr = 0.017/(60*60) #from the paper
HC_yerr = 0.028/(60*60)

FW_xerr = 0.1/(60*60)
FW_yerr = 0.1/(60*60)

RAs = [float(data['RA_FW2011'][ind20] - data['RA_FW2011'][ind_ref]),float(data['RA_HC'][ind20] - data['RA_HC'][ind_ref]),float(data['gauss_x_B3'][ind20] - data['gauss_x_B3'][ind_ref]),float(data['RA_LML'][ind20] - data['RA_LML'][ind_ref]),float(data['RA_MLLA'][ind20] - data['RA_MLLA'][ind_ref])]
DECs = [float(data['DEC_FW2011'][ind20] - data['DEC_FW2011'][ind_ref]),float(data['DEC_HC'][ind20] - data['DEC_HC'][ind_ref]),float(data['gauss_y_B3'][ind20] - data['gauss_y_B3'][ind_ref]),float(data['DEC_LML'][ind20] - data['DEC_LML'][ind_ref]),float(data['DEC_MLLA'][ind20] - data['DEC_MLLA'][ind_ref])]
RA_err = [FW_xerr,HC_xerr,data['x_err_B3'][ind20],FW_xerr, FW_xerr]
DEC_err = [FW_yerr,HC_yerr,data['y_err_B3'][ind20],FW_yerr, FW_yerr]

FW_date, FW_err = middle_date(12,2007,4,2008)
HC_date = (10,1999)
HC_err = 0.001
B3_date = (10,2017)
B3_err = 0.001
LML_date, LML_err = middle_date(10,2002,12,2002)
MLLA_date, MLLA_err = middle_date(12,1997,3,2000)

dates = [FW_date,HC_date,B3_date,LML_date,MLLA_date]
times = calc_times(dates)

times_err = [FW_err,HC_err,B3_err,LML_err,MLLA_err]

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
