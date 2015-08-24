"""
Python script to create a csv with randomly distributed dots for each job within a census block
Based heavily on racial dot map code avaialble at https://github.com/unorthodox123/RacialDotMap/

Paths to data will have to be adjusted for each computer
"""

import sys
from osgeo import ogr
from shapely.wkb import loads
from shapely.geometry import *
from random import uniform, shuffle
import pandas as pd
import os

dirpath = '<path to directory>'
os.chdir(dirpath)

# Import the module that converts spatial data between formats

sys.path.append(dirpath)
from globalmaptiles import GlobalMercator #Need to have globalmaptiles.py in current directory or else add its directory to path

# Main function that reads the shapefile, obtains the population counts,
# creates a point object for each person by race, and exports to a SQL database.

def main(input_filename, wac_filename, output_filename):
    
    wac = pd.io.parsers.read_csv(wac_filename)
    wac.set_index(wac['w_geocode'],inplace = True)
    
    #Create columns for four megasectors
    
    wac['makers'] = wac['CNS01']+wac['CNS02']+wac['CNS03']+wac['CNS04']+wac['CNS05']+wac['CNS06']+wac['CNS08']
    wac['services'] = wac['CNS07']+wac['CNS14'] + wac['CNS17'] + wac['CNS18']
    wac['professions'] = wac['CNS09'] + wac['CNS10'] + wac['CNS11'] + wac['CNS12'] + wac['CNS13']
    wac['support'] = wac['CNS15'] + wac['CNS16'] + wac['CNS19'] + wac['CNS20']

    assert sum(wac['C000'] -(wac['makers']+wac['services']+wac['professions']+wac['support'])) == 0 or rw[1]['abbrev'] == 'ny'

    #In NY there's one block in Brooklyn with 177000 jobs. It appears to be rounding entries > 100k, which is making the assertion fail.
    #This is the Brooklyn Post Office + Brooklyn Law School + Borough Hall. So maybe weirdness around post office? 

    #Set up outfile as csv
    outf = open(output_filename,'w')
    outf.write('x,y,sect,inctype,quadkey\n')
    
    # Create a GlobalMercator object for later conversions
    
    merc = GlobalMercator()

    # Open the shapefile
    
    ds = ogr.Open(input_filename)
    
    if ds is None:
        print "Open failed.\n"
        sys.exit( 1 )

    # Obtain the first (and only) layer in the shapefile
    
    lyr = ds.GetLayerByIndex(0)

    lyr.ResetReading()

    # Obtain the field definitions in the shapefile layer

    feat_defn = lyr.GetLayerDefn()
    field_defns = [feat_defn.GetFieldDefn(i) for i in range(feat_defn.GetFieldCount())]

    # Obtain the index of the field for the count for whites, blacks, Asians, 
    # Others, and Hispanics.
    
    for i, defn in enumerate(field_defns):
        print defn.GetName()
        #GEOID is what we want to merge on
        if defn.GetName() == "GEOID10":
            fips = i

    # Set-up the output file
    
    #conn = sqlite3.connect( output_filename )
    #c = conn.cursor()
    #c.execute( "create table if not exists people_by_race (statefips text, x text, y text, quadkey text, race_type text)" )

    # Obtain the number of features (Census Blocks) in the layer
    
    n_features = len(lyr)

    # Iterate through every feature (Census Block Ploygon) in the layer,
    # obtain the population counts, and create a point for each person within
    # that feature.

    for j, feat in enumerate( lyr ):
        # Print a progress read-out for every 1000 features and export to hard disk
        
        if j % 1000 == 0:
            #conn.commit()
            print "%s/%s (%0.2f%%)"%(j+1,n_features,100*((j+1)/float(n_features)))
            
        # Obtain total population, racial counts, and state fips code of the individual census block
        blkfips = int(feat.GetField(fips))
        
        try:
            jobs = {'m':wac.loc[blkfips,'makers'],'s':wac.loc[blkfips,'services'],'p':wac.loc[blkfips,'professions'],'t':wac.loc[blkfips,'support']}
        except KeyError:
            #print "no"
#            missing.append(blkfips) #Missing just means no jobs there. Lots of blocks have this.
            continue            
        income = {'l':wac.loc[blkfips,'CE01'],'m':wac.loc[blkfips,'CE02'],'h':wac.loc[blkfips,'CE03']}
        # Obtain the OGR polygon object from the feature

        geom = feat.GetGeometryRef()
        
        if geom is None:
            continue
        
        # Convert the OGR Polygon into a Shapely Polygon
        
        poly = loads(geom.ExportToWkb())
        
        if poly is None:
            continue        
            
        # Obtain the "boundary box" of extreme points of the polygon

        bbox = poly.bounds
        
        if not bbox:
            continue
     
        leftmost,bottommost,rightmost,topmost = bbox
    
        # Generate a point object within the census block for every person by race
        inccnt = 0
        incord = ['l','m','h']
        shuffle(incord)
        
        for sect in ['m','s','p','t']:
            for i in range(int(jobs[sect])):

                # Choose a random longitude and latitude within the boundary box
                # and within the orginial ploygon of the census block
                    
                while True:
                        
                    samplepoint = Point(uniform(leftmost, rightmost),uniform(bottommost, topmost))
                        
                    if samplepoint is None:
                        break
                    
                    if poly.contains(samplepoint):
                        break
        
                x, y = merc.LatLonToMeters(samplepoint.y,samplepoint.x)
                tx,ty = merc.MetersToTile(x, y, 21)
                    
                    
                #Determine the right income
                inccnt += 1
                inctype = ''
                assert inccnt <= income[incord[0]] + income[incord[1]] + income[incord[2]] or rw[1]['abbrev'] == 'ny'
                if inccnt <= income[incord[0]]:
                    inctype = incord[0]
                elif inccnt <= income[incord[0]] + income[incord[1]]:
                    inctype = incord[1]
                elif inccnt <= income[incord[0]] + income[incord[1]] + income[incord[2]]:
                    inctype = incord[2]
                        
                # Create a unique quadkey for each point object
                    
                quadkey = merc.QuadTree(tx, ty, 21)       
                 
                outf.write("%s,%s,%s,%s,%s\n" %(x,y,sect,inctype,quadkey))
                # Convert the longitude and latitude coordinates to meters and
                # a tile reference

    outf.close() 
    
       
 
#Link fips to abbreviations
fips2abbrev = pd.io.parsers.read_csv('fips2abbrev.csv')
fips2abbrev.dropna(inplace = True)   
fips2abbrev['abbrev'] = fips2abbrev['abbrev'].str.lower()
fips2abbrev['fips'] =  fips2abbrev['fips'].apply(lambda x: "%02d" %x)


for rw in fips2abbrev.loc[1:2].iterrows(): #
    
    wac_filename = 'data/wac/%s_wac_2010.csv' %rw[1]['abbrev']
    input_filename = 'data/tabblock/tl_2010_%s_tabblock10 Folder/tl_2010_%s_tabblock10.shp' %(rw[1]['fips'],rw[1]['fips'])
    output_filename = 'data/jobpointcsvs/jobpoints_%s_meters.csv' %rw[1]['fips']

    try:
        wac = pd.io.parsers.read_csv(wac_filename)        
    except IOError:
        continue
    
    main(input_filename, wac_filename, output_filename)
