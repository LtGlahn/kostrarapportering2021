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

# Tunneller (evt tunnelløp) som overlapper med høydebegrensning under 4m
overlappfilter  = '591(5277<4)'
mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={ 'overlapp' : overlappfilter } )

# Henter tunneler
sok = nvdbapiv3.nvdbFagdata( 581)
sok.filter( mittfilter )
tunnelGdf = nvdbgeotricks.records2gdf( sok.to_records() )
tunnelGdf.to_file( 'tunneldebug.gpkg', layer='tunnelpunkt_u_4m', driver='GPKG' )

# Dessverre er det noen tunneller som mangler egnenskapen "Lengde, offisiell"
# Vi skal supplere manglende data fra tunnelløp 
# aller først deler vi tunnel-datasettet i to
manglerLengde   = tunnelGdf[  tunnelGdf['Lengde, offisiell'].isnull() ].copy()
harLengde       = tunnelGdf[ ~tunnelGdf['Lengde, offisiell'].isnull() ]

# Først få tak i tunnelløp 
sok = nvdbapiv3.nvdbFagdata( 67 )
sok.filter( mittfilter  ) 
tLopGdf = nvdbgeotricks.records2gdf( sok.to_records( ) )
tLopGdf.to_file( 'tunneldebug.gpkg', layer='tunnelpunkt_u_4m', driver='GPKG' )

# Lager en buffer rundt tunnel (punktobjekt) og gjør geografisk join 
manglerLengde['geometry'] = manglerLengde['geometry'].apply( lambda x : x.buffer( 10, resolution=16) )
geojoin = gpd.sjoin( manglerLengde, tLopGdf, how='inner', op='intersects' )

# Henter Lengde-egenskapverdi 
geojoin['Lengde, offisiell'] = geojoin['Lengde']

# Døper om kolonnenavn så de matcher med orginaldatasettet (tunnel)
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
                'trafikantgruppe_left' : 'trafikantgruppe'
                }

geojoin.rename( columns=oversett, inplace=True )

# Finner felles kolonnenavn
colA = set( harLengde.columns)
colB = set( geojoin.columns)
col = list( colA & colB )
tunnelGdfV2 = pd.concat( [ harLengde, geojoin[col] ] )


telling = tunnelGdfV2.groupby( ['fylke' ]).agg( { 'nvdbId': 'nunique', 'Lengde, offisiell' : 'sum'} ).reset_index()
telling.rename( columns={ 'nvdbId' : 'Antall', 'Lengde, offisiell' : 'Lengde (m)' }, inplace=True )

skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2021/Kostra 16 - tunnell u 4m.xlsx', sheet_name='Tunnel u 4m', metadata=mittfilter)

tidsbruk = datetime.now() - t0 
print( f"tidsbruk kostra rapport 16: {tidsbruk.total_seconds()} sekunder")