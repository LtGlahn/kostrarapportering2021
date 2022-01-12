from datetime import datetime 

import geopandas as gpd 

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbgeotricks

t0 = datetime.now()

mittfilter = lastnedvegnett.filtersjekk(  )
mittfilter['vegsystemreferanse'] = 'Fv'
# mittfilter.pop( 'kryssystem', None )
mittfilter.pop( 'sideanlegg', None )

myGdf = nvdbgeotricks.firefeltrapport( mittfilter=mittfilter, felttype='K' )
myGdf['Lengde kollektivfelt'] = myGdf['kollektivfelt_antsider'] * myGdf['lengde']
statistikk = myGdf.groupby( ['fylke'] ).agg( { 'lengde' : 'sum', 'Lengde kollektivfelt' : 'sum' } ).astype(int).reset_index()
statistikk.rename(  columns={ 'lengde' : 'Lengde en retning (m)',  'Lengde kollektivfelt' : 'Lengde per kollektivfelt (m)'  }, inplace=True  )


# myGdf.to_file( 'kostraleveranser.gpkg', layer='kollektivfelt', driver='GPKG')
# myGdf  = gpd.read_file( 'kostraleveranser.gpkg', layer='kollektivfelt')

skrivdataframe.skrivdf2xlsx( statistikk, '../kostraleveranse2021/Kostra 25 - Fylkesveg med kollektivfelt.xlsx', sheet_name='Fylkesveg med kollektivfelt', metadata=mittfilter)


tidsbruk = datetime.now() - t0 