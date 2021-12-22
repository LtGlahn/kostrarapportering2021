from datetime import datetime 

import geopandas as gpd 
import pandas as pd
import numpy as np
from copy import deepcopy

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3

t0 = datetime.now()

mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={}  )
mittfilter['egenskap'] = '1216=3615'

sok = nvdbapiv3.nvdbFagdata( 241 )
sok.filter( mittfilter )
data = sok.to_records( )
mydf = pd.DataFrame( data )

mydf_K = mydf[ mydf['trafikantgruppe'] == 'K' ]
mydf_G = mydf[ mydf['trafikantgruppe'] == 'G' ]

# Debugger, sjekker lengde per vegnummer
# lengde = mydf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
# lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
# lengde['Lengde (m)'] = lengde['segmentlengde']
# lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

tellingK = mydf_K.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
tellingG = mydf_G.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
tellingK.rename( columns={ 'segmentlengde' : 'Lengde kjøreveg (m)'}, inplace=True )
tellingG.rename( columns={ 'segmentlengde' : 'Lengde gang/sykkelveg (m)'}, inplace=True )


skrivdataframe.skrivdf2xlsx( [tellingK, tellingG], '../kostraleveranse2021/Kostra 03 - Fylkesveg uten fast dekke.xlsx', 
    sheet_name=[ 'Fv grus kjørende', 'Fv grus G S'], metadata=mittfilter)

tidsbruk = datetime.now() - t0 
print( f"Kjøretid  {tidsbruk.total_seconds()} sekunder " )