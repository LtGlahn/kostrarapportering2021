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
mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : '5277 < 4 AND 5270=8151' } )
# mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : ' 5277 < 4 AND ( 5270=8168 OR 5270=8149 ) ', 'overlapp' : '60(1263=7304)'} )
# mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'overlapp' : '591(5277 < 4 AND ( 5270=8168 OR 5270=8149 ) ) ', 'egenskap' : '1263=7304'} )
sok = nvdbapiv3.nvdbFagdata( 591 )
sok.filter( mittfilter  ) 
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) )

# myGdf.to_file(  'brudebug.gpkg', layer='nyeHoydeBegrBruer', driver='GPKG')

# Debugger hvilken effekt overlapp med bru evt måtte ha... 
filter2 = deepcopy( mittfilter )
filter2['overlapp'] = '60'
sok = nvdbapiv3.nvdbFagdata( 591 )
sok.filter( filter2 )
testGdf = nvdbgeotricks.records2gdf( sok.to_records())


telling = myGdf.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique' } ).astype(int).reset_index()
telling.rename( columns={ 'nvdbId' : 'Antall', 'lengde' : 'Lengde (m)' }, inplace=True )


skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 09 - Undergang lavere enn 4m.xlsx', sheet_name='Undergang lavere enn 4m', metadata=mittfilter)

tidsbruk = datetime.now() - t0 