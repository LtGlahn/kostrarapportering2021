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

#  EnumNotInSetProvider(904, 10901, 18184, 18186)  
# 
# 10901, # Bruksklasse 10901  
# 18187, # BkT8 - 40 tonn 18187         egenskap(10901)=18187
# 18188, # Bk8 - 32 tonn 18188          egenskap(10901)=18188
# 18189, # Bk6 - 28 tonn 18189          egenskap(10901)=18189
# 18190, # Spesiell begrensning 18190   egenskap(10901)=18190 
# Bk10 - 42 tonn 18185                  egenskap(10901)=18185  
# 
# Bk10 - 50 tonn 18184                  egenskap(10901)=18184  NEI
# 18186, # BkT8 - 50 tonn 18186         egenskap(10901)=18186 NEI

# 
# Eks bygge spørring: egenskap(10278)>=2000 AND egenskap(1313)<=100


egenskapfilter = 'egenskap(10901)=18187 OR egenskap(10901)=18188 OR egenskap(10901)=18189 OR egenskap(10901)=18190 OR egenskap(10901)=18185'


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

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 06 - Fylkesveg totalvekt u 50t.xlsx', sheet_name='Fv totalvekt u 50t', metadata=mittfilter)

tidsbruk = datetime.now() - t0 
print( f"Kjøretid  {tidsbruk.total_seconds()} sekunder " )