#%%
from datetime import datetime 

import geopandas as gpd 

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbgeotricks 

t0 = datetime.now()

mittfilter = lastnedvegnett.filtersjekk(  )
mittfilter['vegsystemreferanse'] = 'Fv'

myGdf = lastnedvegnett.vegnetthelelandet( mittfilter=mittfilter )
myGdf.to_file( 'vegnetthelelandet.gpkg', layer='norge', driver='GPKG')
# myGdf  = gpd.read_file( 'vegnetthelelandet.gpkg', layer='norge')

# lastnedvegnett.rapport01_gdf2excel( myGdf, filnavn='../kostraleveranse2021/Kostra 01 - Vegnett hele landet.xlsx', metadata=mittfilter)

tidsbruk = datetime.now() - t0 


def tellfelt( feltoversikt ):
    felt = feltoversikt.split(',')
    count = 0
    for etfelt in felt:
        if 'O' in etfelt or 'H' in etfelt or 'V' in etfelt or 'S' in etfelt:
            pass
        else:
            count += 1
    return count
myGdf['antallfelt'] = myGdf['feltoversikt'].apply( tellfelt )
minAgg = myGdf.groupby( ['fylke'] ).agg( {'lengde' : 'sum', 'feltlengde' : 'sum' } ).reset_index()
minAgg

skrivdataframe.skrivdf2xlsx( minAgg, 'veglengerSept2022.xlsx')


#%% 

print( "Hei og hopp")
# %%
