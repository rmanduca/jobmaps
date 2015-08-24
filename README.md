Guide to making the dot maps

1) Download wac files (at http://lehd.ces.census.gov/data/#lodes) and 2010 Census Block shapefiles (from https://www.census.gov/cgi-bin/geo/shapefiles2010/main)

2) Run "dotfile_wac.py" on a computer with GEOS. This creates one csv for each state with points for jobs that are categorized by quadkey and by type of job. 

3) Run "sort_by_quadkey.py". This combines all the csvs into one big csv that is sorted by quadkey.

4) When I ran this there were two lines at the end of the quadkey file that were incorrect. I deleted them manually--they are missing some important data. You can see them by doing tail all_meters.csv in the terminal. You can delete them by running sed '125126130,125126131d' all_meters.csv > all_meters_trimmed.csv (substitute the proper numbers)

5) Run the Processing file dotmap_server.pde. 

6) Copy over tiles to the website and set up the website. Make sure to turn off the automatic spelling correction on the server or else it will put tiles in the wrong place.