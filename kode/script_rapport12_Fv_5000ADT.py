from datetime import datetime 

import geopandas as gpd 
import pandas as pd
import numpy as np
from copy import deepcopy

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3
import nvdbgeotricks

t0 = datetime.now()

filter2 = lastnedvegnett.kostraFagdataFilter(mittfilter={}  )
filter2['egenskap'] = '4623>=5000' 

sok = nvdbapiv3.nvdbFagdata( 540)
sok.filter( filter2 )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 
myGdf.to_file( 'debug_grus.gpkg', layer='AADT alt over 5000', driver='GPKG')

# Debugger, sjekker lengde per vegnummer
lengde = myGdf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
lengde['Lengde (m)'] = lengde['segmentlengde']
lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

telling = myGdf.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).reset_index()  

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 12 - Fylkesveg ÅDT over 5000.xlsx', sheet_name='Fv over 5000ÅDT', metadata=filter2)

tidsbruk = datetime.now() - t0 