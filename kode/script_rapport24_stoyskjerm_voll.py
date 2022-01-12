from datetime import datetime 
from copy import deepcopy 

import geopandas as gpd 
import pandas as pd
import numpy as np

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3

t0 = datetime.now()
skjermfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : '1247=1994'} )
skjermsok = nvdbapiv3.nvdbFagdata( 3 )
skjermsok.filter( skjermfilter ) 
skjerm = pd.DataFrame( skjermsok.to_records( ) )
skjermlengde = skjerm.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'segmentlengde' : 'sum' } ).reset_index()
skjermlengde.rename( columns={ 'nvdbId' : 'Antall', 'segmentlengde' : 'Lengde (m)' }, inplace=True )

vollfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : '1286=1996'} )
vollsok = nvdbapiv3.nvdbFagdata( 234 )
vollsok.filter( vollfilter ) 
voll = pd.DataFrame( vollsok.to_records( ) )
volllengde = voll.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'segmentlengde' : 'sum' } ).reset_index()
volllengde.rename( columns={ 'nvdbId' : 'Antall', 'segmentlengde' : 'Lengde (m)' }, inplace=True )

# lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
# lengde['Lengde (m)'] = lengde['segmentlengde']
# lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

mittfilter = deepcopy( skjermfilter )
egfilter_skjerm = mittfilter.pop( 'egenskap' )
mittfilter['egenskapsfilter 3 Skjerm'] = egfilter_skjerm
mittfilter['egenskapsfilter 234 Voll'] = vollfilter['egenskap']


skrivdataframe.skrivdf2xlsx( [ skjermlengde, volllengde ], '../kostraleveranse2021/Kostra 24 - Fylkesveg med stoyskjerm og voll.xlsx', sheet_name=['Fylkesveg med støyskjerm', 'Fylkesveg med voll' ], metadata=mittfilter)

tidsbruk = datetime.now() - t0 