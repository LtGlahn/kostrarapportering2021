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

mittfilter = lastnedvegnett.kostraFagdataFilter(  )
mittfilter['egenskap'] = '1216=3615'
mittfilter['overlapp'] = '540(4623>=5000)'

sok = nvdbapiv3.nvdbFagdata( 241 )
sok.filter( mittfilter )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 

myGdf.to_file( 'debug_grus.gpkg', layer='grus aadt over 5000', driver='GPKG' )

# Debugger, henter det inverse søket. 
filter2 = lastnedvegnett.kostraFagdataFilter(mittfilter={}  )
filter2['overlapp'] = '241(1216=3615)' 
filter2['egenskap'] = '4623>=5000' 

sok = nvdbapiv3.nvdbFagdata( 540)
sok.filter( filter2 )
aadt_Gdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 
aadt_Gdf.to_file( 'debug_grus.gpkg', layer='AADT over 5000 grus', driver='GPKG')

# Debugger, sjekker lengde per vegnummer
lengde = myGdf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
lengde['Lengde (m)'] = lengde['segmentlengde']
lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

telling = myGdf.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).reset_index()  
telling.rename( columns={ 'segmentlengde' : 'Lengde (m)' }, inplace=True)

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 11 - Fylkesveg uten fast dekke ÅDT over 5000.xlsx', sheet_name='Fv grus over 5000ÅDT', metadata=mittfilter)

tidsbruk = datetime.now() - t0 