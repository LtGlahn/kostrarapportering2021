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

# Teller motorveg av klasse A og motortrafikkveg


# mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={} )
mittfilter = { 'tidspunkt': '2021-12-15'}
# mittfilter['adskiltelop'] = 'med,nei'
# mittfilter['sideanlegg'] = 'false'

sok = nvdbapiv3.nvdbFagdata( 595  )
sok.filter( mittfilter )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 

myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']    # Kun kjørende 
myGdf = myGdf[ myGdf['adskilte_lop'] != 'Mot' ]     # Adskilte løp = Med,Nei 
myGdf = myGdf[ ~myGdf['vref'].str.contains( 'SD') ] # Fjerner sideanlegg
myGdf = myGdf[ ~myGdf['vref'].str.contains( 'KD') ] # Fjerner kryssdeler
myGdf = myGdf[ myGdf['typeVeg'] != 'Rampe' ] # Fjerner ramper 



# # For debugging 
# lengde = myGdf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
# lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
# lengde['Lengde (m)'] = lengde['segmentlengde']
# lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

telling = myGdf.groupby( ['fylke', 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
telling.rename( columns={ 'segmentlengde' : 'Lengde (m)' }, inplace=True)
lengde = myGdf.groupby( [ 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()
print( "Motorveg i i fjor", lengde)

metadata = { 'tidspunkt' : '2021-12-15', 'Kryssdeler' : 'Kryssdeler filtrert vekk', 'Sideanlegg' : 'Sideanlegg filtrert vekk', 'Ramper' : 'Ramper filtrert vekk', 'trafikantgruppe' : 'K' }
skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/EKSTRARAPPORT motorveger.xlsx', sheet_name='Motorveger', metadata=metadata )


tidsbruk = datetime.now() - t0 

# Debugger og sammenligner med i dag
myGdf.to_file( 'debugmotorveg.gpkg', layer='motorveg-2021-12-15', driver='GPKG')



sok = nvdbapiv3.nvdbFagdata( 595  )
myGdf2 = nvdbgeotricks.records2gdf( sok.to_records( ) ) 
myGdf2 = myGdf2[ myGdf2['trafikantgruppe'] == 'K']    # Kun kjørende 
myGdf2 = myGdf2[ myGdf2['adskilte_lop'] != 'Mot' ]     # Adskilte løp = Med,Nei 
myGdf2 = myGdf2[ ~myGdf2['vref'].str.contains( 'SD') ] # Fjerner sideanlegg
myGdf2 = myGdf2[ ~myGdf2['vref'].str.contains( 'KD') ] # Fjerner kryssdeler
myGdf2 = myGdf2[ myGdf2['typeVeg'] != 'Rampe' ] # Fjerner ramper

telling2 = myGdf2.groupby( ['fylke', 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()
lengde2 = myGdf2.groupby( [ 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()
print( "Motorveg i dag", lengde2)

myGdf2.to_file( 'debugmotorveg.gpkg', layer='motorveg-2022-05-03', driver='GPKG')
