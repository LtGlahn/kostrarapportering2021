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
mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'overlapp' : '591(5277 < 4 AND (5270=8168 OR 5270=8149))', 'egenskap' : '1263=7304'} )
# mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : ' 5277 < 4 AND ( 5270=8168 OR 5270=8149 ) ', 'overlapp' : '60(1263=7304)'} )
# mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'overlapp' : '591(5277 < 4 AND ( 5270=8168 OR 5270=8149 ) ) ', 'egenskap' : '1263=7304'} )
sok = nvdbapiv3.nvdbFagdata( 60 )
sok.filter( mittfilter  ) 
bruGdf = nvdbgeotricks.records2gdf( sok.to_records( ) )

bruGdf.to_file(  'brudebug.gpkg', layer='nyeHoydeBegrBruer', driver='GPKG')

# Oppsummerer bru. Her må vi ta hensyn til at noen av bruene mangler egenskapen "Lengde" 
bruGdf_medLengde = bruGdf[ ~bruGdf['Lengde'].isnull() ].drop_duplicates( subset='nvdbId')
bruGdf_uLengde =   bruGdf[  bruGdf['Lengde'].isnull() ].copy()
bruGdf_uLengde['Lengde'] = bruGdf_uLengde['segmentlengde']
bru_alleharLengde = pd.concat( [ bruGdf_medLengde, bruGdf_uLengde ]  )

telling = bru_alleharLengde.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'Lengde' : 'sum'} ).reset_index()
telling.rename( columns={ 'nvdbId' : 'Antall', 'lengde' : 'Lengde (m)' }, inplace=True )


skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 19 - Bruer hoyde mindre enn 4m.xlsx', sheet_name='Bru høydebegrensning under 4m', metadata=mittfilter)

tidsbruk = datetime.now() - t0 