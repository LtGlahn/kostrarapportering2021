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

# Henter alle tunneler 
mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={}  )

# Henter tunneller 
sok = nvdbapiv3.nvdbFagdata( 581)
sok.filter( mittfilter )
tunnelGdf = nvdbgeotricks.records2gdf( sok.to_records() )
tunnelGdf.to_file( 'tunneldebug.gpkg', layer='alletunneller', driver='GPKG' )

# Dessverre er det noen tunnelløp som mangler egnenskapen "Lengde, offisiell"
# Vi skal supplere manglende data fra tunnelløp 
# aller først deler vi tunnel-datasettet i to
manglerLengde   = tunnelGdf[  tunnelGdf['Lengde, offisiell'].isnull() ].copy()
harLengde       = tunnelGdf[ ~tunnelGdf['Lengde, offisiell'].isnull() ]

# Først få tak i tunnelløp 
sok = nvdbapiv3.nvdbFagdata( 67 )
sok.filter( mittfilter  ) 
tLopGdf = nvdbgeotricks.records2gdf( sok.to_records( ) )
tLopGdf.to_file( 'tunneldebug.gpkg', layer='alletunnellop', driver='GPKG' )

# Tar vare på geometrilengden 
tLopGdf['geometrilengde'] = tLopGdf['geometry'].apply( lambda x : x.length )

# Lager en buffer rundt tunnel (punktobjekt) og gjør geografisk join 
manglerLengde['geometry'] = manglerLengde['geometry'].apply( lambda x : x.buffer( 10, resolution=16) )
geojoin = gpd.sjoin( manglerLengde, tLopGdf, how='inner', op='intersects' )

# Har vi lengde-egenskap? Del datasettet i to. 
lop_harLengde       = geojoin[ ~geojoin['Lengde'].isnull( )].copy()
lop_manglerLengde   = geojoin[  geojoin['Lengde'].isnull( )].copy()

# Henter Lengde-egenskapverdi 
lop_harLengde['Lengde, offisiell'] = lop_harLengde['Lengde']


# Henter lengde fra geometri-egenskap
lop_manglerLengde['Lengde, offisiell'] = lop_manglerLengde['geometrilengde']


# Døper om kolonnenavn så de matcher med orginaldatasettet (tunnel)
col = list( tunnelGdf.columns )
oversett = {    'objekttype_left' : 'objekttype',
                'nvdbId_left' : 'nvdbId',
                'versjon_left' : 'versjon',
                'startdato_left' : 'startdato',
                'Åpningsår_left' : 'Åpningsår',
                'Navn_left' : 'Navn',
                'veglenkesekvensid_left' : 'veglenkesekvensid',
                'detaljnivå_left' : 'detaljnivå',
                'typeVeg_left' : 'typeVeg',
                'kommune_left' : 'kommune',
                'fylke_left' : 'fylke',
                'vref_left' : 'vref',
                'vegkategori_left' : 'vegkategori',
                'fase_left' : 'fase',
                'nummer_left' : 'nummer',
                'adskilte_lop_left' : 'adskilte_lop',
                'trafikantgruppe_left' : 'trafikantgruppe', 
                'Prosjektreferanse_left' : 'Prosjektreferanse', 
                'Brutus_Id_left' :   'Brutus_Id',
                'sluttdato_left' :  'sluttdato'
                }

lop_manglerLengde.rename( columns=oversett, inplace=True )
lop_harLengde.rename( columns=oversett, inplace=True )

tunnelGdfV2 = pd.concat( [ harLengde, lop_manglerLengde[col], lop_harLengde[col] ] )



telling = tunnelGdfV2.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'Lengde, offisiell' : 'sum'} ).astype(int).reset_index()
telling.rename( columns={ 'nvdbId' : 'Antall', 'Lengde, offisiell' : 'Lengde (m)' }, inplace=True )

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 13 og 14 - tunnell fylkesveg.xlsx', sheet_name='Tunnel Fv', metadata=mittfilter)

langeTunneller = tunnelGdfV2[ tunnelGdfV2['Lengde, offisiell'] >= 500 ]
telling = langeTunneller.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'Lengde, offisiell' : 'sum'} ).astype(int).reset_index()
telling.rename( columns={ 'nvdbId' : 'Antall', 'Lengde, offisiell' : 'Lengde (m)' }, inplace=True )

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 15 - tunnell lengre enn 500m.xlsx', sheet_name='Tunnel lengre enn 500m', metadata=mittfilter)


tidsbruk = datetime.now() - t0 