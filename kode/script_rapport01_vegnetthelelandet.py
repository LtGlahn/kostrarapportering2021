from datetime import datetime 

import geopandas as gpd 

import STARTHER
import lastnedvegnett  
import skrivdataframe

t0 = datetime.now()

mittfilter = lastnedvegnett.filtersjekk(  )
mittfilter['vegsystemreferanse'] = 'Ev,Rv,Fv,Kv,Sv,Pv'

myGdf = lastnedvegnett.vegnetthelelandet( mittfilter=mittfilter )
myGdf.to_file( 'vegnetthelelandet.gpkg', layer='norge', driver='GPKG')
# myGdf  = gpd.read_file( 'vegnetthelelandet.gpkg', layer='norge')

lastnedvegnett.rapport01_gdf2excel( myGdf, filnavn='../kostraleveranse2021/Kostra 01 - Vegnett hele landet.xlsx', metadata=mittfilter)

tidsbruk = datetime.now() - t0 