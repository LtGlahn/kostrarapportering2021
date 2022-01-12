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
sterkfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'egenskap' : '9500=13384'} )
vegmerksok = nvdbapiv3.nvdbFagdata( 836 )
vegmerksok.filter( sterkfilter ) 
vegmerk = pd.DataFrame( vegmerksok.to_records( ) )
vegmerklendge = vegmerk.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'segmentlengde' : 'sum' } ).reset_index()
vegmerklendge.rename( columns={ 'nvdbId' : 'Antall', 'segmentlengde' : 'Lengde (m)' }, inplace=True )


skrivdataframe.skrivdf2xlsx( vegmerklendge, '../kostraleveranse2021/Kostra 23 - Fylkesveg med forsterket midtoppmerking.xlsx', 
                                sheet_name='FV med forsterket vegmerking', metadata=sterkfilter)

tidsbruk = datetime.now() - t0 