from datetime import datetime 
from copy import deepcopy 

import geopandas as gpd 
import pandas as pd
import numpy as np

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3
import nvdbgeotricks

t0 = datetime.now()

# egenskapfilter_bk904_u10t = 'egenskap(10901)=18186 OR egenskap(10901)=18187 OR egenskap(10901)=18188 OR egenskap(10901)=18189 OR egenskap(10901)=18190'
# overlappfilter  = '904(10901=18186 OR 10901=18187 OR 10901=18188 OR 10901=18189 OR 10901=18190)'

mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : '1263=7304 OR 1263=7305'  } )
sok = nvdbapiv3.nvdbFagdata( 60 )
sok.filter( mittfilter  ) 
bruGdf = nvdbgeotricks.records2gdf( sok.to_records( ) )

# Oppsummerer bru. Her må vi ta hensyn til at noen av bruene mangler egenskapen "Lengde" 
bruGdf_medLengde = bruGdf[ ~bruGdf['Lengde'].isnull() ].drop_duplicates( subset='nvdbId')
bruGdf_uLengde =   bruGdf[  bruGdf['Lengde'].isnull() ].copy()
bruGdf_uLengde['Lengde'] = bruGdf_uLengde['segmentlengde']
bru_alleharLengde = pd.concat( [ bruGdf_medLengde, bruGdf_uLengde ]  )

telling = bru_alleharLengde.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'Lengde' : 'sum'} ).reset_index()
telling.rename( columns={ 'nvdbId' : 'Antall', 'lengde' : 'Lengde (m)' }, inplace=True )

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 17 - Bruer fylkesveg.xlsx', sheet_name='Bruer fylkesveg', metadata=mittfilter)

tidsbruk = datetime.now() - t0 