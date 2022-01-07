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

#  EnumInSetProvider(904, 10913, 18256, 18254, 18255)
# 
# 19,50 18253 < Ikke denna, men resten
# 15,00 18254
# 12,40 18255
# Spesiell begrensning 18256


egenskapfilter = 'egenskap(10913)=18254 OR egenskap(10913)=18255 OR egenskap(10913)=18256'

mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={} )
mittfilter['vegsystemreferanse'] = 'Fv'
mittfilter['egenskap'] = egenskapfilter
mittfilter['adskiltelop'] = 'med,nei'
mittfilter['sideanlegg'] = 'false'


sok = nvdbapiv3.nvdbFagdata( 904 )
sok.filter( mittfilter )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 

myGdf_G = myGdf[ myGdf['trafikantgruppe'] == 'G'].copy()
myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']

# For debugging 
lengde = myGdf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
lengde['Lengde (m)'] = lengde['segmentlengde']
lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

telling = myGdf.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
telling.rename( columns={ 'segmentlengde' : 'Lengde (m)' }, inplace=True)

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 08 - maks lengde u 19m.xlsx', sheet_name='Fv lengde u 19,5m', metadata=mittfilter)

tidsbruk = datetime.now() - t0 