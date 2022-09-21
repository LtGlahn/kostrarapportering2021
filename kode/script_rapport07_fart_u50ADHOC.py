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

#  EnumInSetProvider(105, 2021, 2726, 2728, 11576, 2730, 19885)//TODO: la til 5km/t i listen. Skjekk om det er riktig!
# 
# 
# Eks bygge spørring: egenskap(10278)>=2000 AND egenskap(1313)<=100


egenskapfilter = 'egenskap(2021)=2726 OR egenskap(2021)=2728 OR egenskap(2021)=11576 OR egenskap(2021)=2730 OR egenskap(2021)=19885'


mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={} )
mittfilter.pop( 'tidspunkt', None ) # ADHOC 

mittfilter['vegsystemreferanse'] = 'Fv'
mittfilter['egenskap'] = egenskapfilter
mittfilter['adskiltelop'] = 'med,nei'
mittfilter['sideanlegg'] = 'false'

sok = nvdbapiv3.nvdbFagdata( 105 )
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

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 07 - Fylkesveg maks 50kmtADHOC.xlsx', sheet_name='Fv 50km eller lavere', metadata=mittfilter)

tidsbruk = datetime.now() - t0 
print( f"Tidsbruk {tidsbruk} ")