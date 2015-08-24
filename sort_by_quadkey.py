"""
Python script to sort points by quadkey
Outputs one giant (multi-gig) csv with a lat long for every job
Paths may need to be adjusted depending on folder structure
"""

import sys
import pandas as pd
import os

#Bring in all the data from before and sort it by quadkey

dirpath = '<path to directory>'
os.chdir(dirpath)

#Link fips to abbreviations
fips2abbrev = pd.io.parsers.read_csv('fips2abbrev.csv')
fips2abbrev.dropna(inplace = True)   
fips2abbrev['abbrev'] = fips2abbrev['abbrev'].str.lower()
fips2abbrev['fips'] =  fips2abbrev['fips'].apply(lambda x: "%02d" %x)

dat = pd.io.parsers.read_csv('data/jobpointcsvs/jobpoints_01_meters.csv' )

for rw in fips2abbrev.iterrows(): #loc[46:73].
    try:
        newdat = pd.io.parsers.read_csv('data/jobpointcsvs/jobpoints_%s_meters.csv' %rw[1]['fips'])
    except IOError:
        continue
    dat = pd.concat([dat, newdat])
    print rw[1]['fips']
    
dat.sort('quadkey',inplace = True)
dat.to_csv('data/jobpointcsvs/all_meters.csv', index = False)
