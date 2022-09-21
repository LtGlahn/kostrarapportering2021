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
# filter2['egenskap'] = '4623>=5000' 
filter2.pop( 'tidspunkt', None)

sok = nvdbapiv3.nvdbFagdata( 540)
sok.filter( filter2 )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 
myGdf.to_file( 'adhocAADT.gpkg', layer='AADT', driver='GPKG')

# Debugger, sjekker lengde per vegnummer
# lengde = myGdf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
# lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
# lengde['Lengde (m)'] = lengde['segmentlengde']
# lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]



telling = myGdf.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).reset_index()  

# skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 12 - Fylkesveg ÅDT over 5000.xlsx', sheet_name='Fv over 5000ÅDT', metadata=filter2)

tidsbruk = datetime.now() - t0 

myGdf = myGdf[ myGdf['adskilte_lop'] != 'Mot']

over1500adt = myGdf[ myGdf['ÅDT, total'] > 1500 ].groupby( 'fylke' ).agg( {  'segmentlengde'  : 'sum' } ).reset_index()

myGdf['kjoretoyKm'] = myGdf['segmentlengde'] * myGdf['ÅDT, total'] * 365 / 1000
trafikkArb = myGdf.groupby([ 'fylke'] ).agg( {'segmentlengde' : 'sum', 'kjoretoyKm' : 'sum' } ).reset_index()


trafikkArb['Trafikkarbeid (mill kjøretøykm)'] = trafikkArb['kjoretoyKm'] / 1e6
over1500adt.rename( columns={'segmentlengde' : 'Lengde Ådt > 1500 (km)'} , inplace=True)
over1500adt['Lengde Ådt > 1500 (km)'] = over1500adt['Lengde Ådt > 1500 (km)'] / 1000
trafikkArb.rename( columns={'segmentlengde' : 'Lengde m ÅDT-data (km)' }, inplace=True )
trafikkArb['Lengde m ÅDT-data (km)'] = trafikkArb['Lengde m ÅDT-data (km)'] / 1000
trafikkArb.rename( columns={'Lengde m ÅDT-data (km)' : 'Lengde veg som har ÅDT-data'}, inplace=True )

data = pd.merge( trafikkArb, over1500adt, on='fylke' )
skrivdataframe.skrivdf2xlsx( data, 'adhocÅDTanalyse.xlsx' )