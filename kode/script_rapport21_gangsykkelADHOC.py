from datetime import datetime 

import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbgeotricks
import nvdbapiv3

t0 = datetime.now()


mittfilter = {  'trafikantgruppe'       : 'G', 
                'detaljniva'            : 'VT,VTKB',
                'adskiltelop'           : 'med,nei',
                # 'historisk'             : 'true', 
                'vegsystemreferanse'    : 'Fv',
                'veglenketype'          : 'hoved', 
                'typeveg'               : 'kanalisertVeg,enkelBilveg,rampe,rundkjøring,gangOgSykkelveg,sykkelveg,gangveg,gatetun'
                }

myGdf = nvdbgeotricks.vegnett2gdf( mittfilter=mittfilter )

statistikk = myGdf.groupby( ['fylke'] ).agg( { 'lengde' : 'sum' } ).reset_index()

myGdf.to_file( 'sykkelvegADHOC.gpkg', layer='gangsykkelveg-fravegnett', driver='GPKG')

## Sammenligner denne metoden med 532-baserte rutiner. 
sok = nvdbapiv3.nvdbFagdata( 532)
# Vegstatus = G (Gang/sykkelveg) eller U (Midlertidig status gang-/sykkelveg)
# sok.filter( {'alle_versjoner' : True, 'egenskap' : '(4567=12983 OR 4567=12159)' })
# sok.filter( { 'egenskap' : '(4567=12983 OR 4567=12159)', 'tidspunkt' : '2022-12-31'})
sok.filter( { 'egenskap' : '(4567=12983 OR 4567=12159)' })
sok.filter( { 'vegsystemreferanse' : 'Fv' })

vegref = pd.DataFrame( sok.to_records( vegsegmenter=True  ) )
vegref['geometry'] = vegref['geometri'].apply( wkt.loads )
if 'vegsegmenter' in vegref.columns:    
    vegref.drop( columns='vegsegmenter', inplace=True)
vegref = gpd.GeoDataFrame( vegref, geometry='geometry', crs=5973 )



# Fjerner fiktiv veg og konnekteringslenker
vegref = vegref[ vegref['Vegtype'] != 'Fiktiv']
vegref = vegref[ vegref['Konnekteringslenke'] != 'Konnekteringslenke' ]

# Sjekker at vi ikke har to kolonner som begge heter vegkategori
kolonnedubletter = [ i for i, e in enumerate( vegref.columns ) if 'vegkategori' in e.lower() ]
if len( kolonnedubletter ) > 1: 
    vegref.rename( columns={'Vegkategori' : 'Vegkategori532' }, inplace= True )

vegref.to_file( 'sykkelvegADHOC.gpkg', layer='gangsykkelveg-fra532', driver='GPKG')

vegrefstatistikk = vegref.groupby( ['fylke'] ).agg( { 'segmentlengde' : 'sum' } ).reset_index()

altsammen = pd.merge( vegrefstatistikk, statistikk, on='fylke', how='inner')

skrivdataframe.skrivdf2xlsx( [ altsammen ], 'AD HOC TEST Kostra 21 gang og sykkelveg.xlsx', 
    sheet_name='Fylkesveg gang og sykkelveg', metadata=mittfilter)



tidsbruk = datetime.now() - t0 