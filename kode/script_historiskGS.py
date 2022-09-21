from datetime import datetime 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd 
import geopandas as gpd 
from shapely import wkt

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbgeotricks
import nvdbapiv3

t0 = datetime.now()
data = []

# for aar in range( 1990, 2022): 
for aar in [2014, 2019 ]: 

    mittfilter = { 'tidspunkt'              : str(aar) +  '-12-16', 
                    'trafikantgruppe'       : 'G', 
                    'detaljniva'            : 'VT,VTKB',
                    'adskiltelop'           : 'med,nei',
                    'historisk'             : 'true', 
                    'vegsystemreferanse'    : 'Ev,Rv,Fv,Kv,Pv,Sv',
                    'veglenketype'          : 'hoved', 
                    'typeveg'               : 'kanalisertVeg,enkelBilveg,rampe,rundkjøring,gangOgSykkelveg,sykkelveg,gangveg,gatetun'
                    }

    mittfilter = {'tidspunkt' : str(aar) +  '-12-16'  }
    sok = nvdbapiv3.nvdbVegnett()
    mydf = pd.DataFrame( sok.to_records( ) )
    print( "Trafikantgruppe-antall for år", aar, '\n', mydf['trafikantgruppe'].value_counts( dropna=False ) )

    col = [ 'kortform', 'veglenkenummer', 'type', 'detaljnivå', 'typeVeg', 
           'målemetode', 'feltoversikt', 'geometri', 'lengde', 'fylke', 'kommune',
        'vref', 'vegkategori',
       'fase', 'nummer',   'trafikantgruppe', 'medium', 'måledato',
       'superstedfesting', 'startdato' ]

    if 'sluttdato' in mydf.columns: 
        col.append( 'sluttdato')
    else: 
        print( f"Ingen sluttdato registrert for datauttak {mittfilter['tidspunkt']} ")

    mydf = mydf[ mydf['trafikantgruppe'] == 'G'][col].copy()
    mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )
    myGdf['Dato'] = mittfilter['tidspunkt']

    # myGdf = nvdbgeotricks.vegnett2gdf( mittfilter=mittfilter )
    if isinstance( myGdf, gpd.GeoDataFrame) and len( myGdf ) > 0: 

        statistikk = myGdf.groupby( ['vegkategori', 'fylke'] ).agg( { 'lengde' : 'sum' } ).reset_index()
        statistikk['Dato'] = mittfilter['tidspunkt']
        data.append ( statistikk  )

        myGdf.to_file( 'sykkelveghistorikk.gpkg', layer='gangsykkelveg' + str( aar ), driver='GPKG')

    tidsbruk = datetime.now() - t0 

    print( f"{tidsbruk} sekunder for år {aar}")