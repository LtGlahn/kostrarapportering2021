from datetime import datetime 
from copy import deepcopy
import requests

import geopandas as gpd 
import pandas as pd
import numpy as np
from shapely import wkt 

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3
import nvdbgeotricks

def hentKjfelt( myRow, veger ): 
    """
    henter kjørefelt fra (geo)dataframe veger som matcher veglenkeposisjoner til myRow

    forutsetter at metoden finnAntallFelt er kjørt først på veger-dataframe 
    veger['kjfelt'] = veger['feltoversikt'].apply( lambda x : finnAntallFelt( x ) ) 

    """

    myVeger = veger[ (veger['veglenkesekvensid'] == myRow['veglenkesekvensid']) & (veger['startposisjon'] < myRow['sluttposisjon']) & (veger['sluttposisjon'] > myRow['startposisjon'] ) ]
    kjfelt = sorted( list( set( list(  myVeger['kjfelt']  ))))
    tekst = ','.join( kjfelt )
    return tekst


t0 = datetime.now()

#  EnumInSetProvider(5, 1248, 11789),

def finnAntallFelt( feiltoversikt ): 
    if isinstance( feiltoversikt, list ):
        feltFiltrering = nvdbgeotricks.filtrerfeltoversikt( feiltoversikt, mittfilter=['vanlig', 'K'] )

        # Skal ha felt i begge retninger (1 og 2), og enten to eller tre felt 
        if len( feltFiltrering ) in [ 2, 3 ] and 1 in feltFiltrering and 2 in feltFiltrering: 
            return '2-3felt'
        elif len( feltFiltrering ) < 2:
            return 'Ettfelt'
        elif len( feltFiltrering ) > 3:
            return 'mangefelt'

    elif np.isnan( feiltoversikt ): 
        return 'ukjent'
    else: 
        print( 'Fikk rar datatype???', str( type( feiltoversikt )))
    return 'ukjent'

egenskapfilter = 'egenskap(1248)=11788 OR egenskap(1248)=11789'


mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={} )
mittfilter['vegsystemreferanse'] = 'Fv'
mittfilter['egenskap'] = egenskapfilter
mittfilter['adskiltelop'] = 'med,nei'
mittfilter['sideanlegg'] = 'false'

sok = nvdbapiv3.nvdbFagdata( 5 )
sok.filter( mittfilter )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 

myGdf_G = myGdf[ myGdf['trafikantgruppe'] == 'G'].copy()
myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K'].copy()
# kun 60 objekt, det var ikke all verden... 


# Henter veglenkesekvenser ut fra ID 
veglenkesekvensId = list( set( list(  myGdf['veglenkesekvensid'] ) ) ) 
veglenker = [ ]

url = 'https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/segmentert/'
headers = {  'Accept' : 'application/vnd.vegvesen.nvdb-v3-rev1+json', 'X-Client' : 'jajens python'  }
params = { 'historisk' : True }
for veg in veglenkesekvensId: 
    veglenker.extend(  requests.get(  url + str( veg ), params=params,  headers=headers ).json() )

veger = pd.DataFrame( veglenker )
# Filtrerer på dato, skal ha veger gyldige 31.12.2020
veger['d1'] = veger['metadata'].apply( lambda x : datetime.strptime(  x['startdato'], '%Y-%m-%d' ) )
veger['d2'] = veger['metadata'].apply( lambda x : datetime.strptime(  x['sluttdato'], '%Y-%m-%d' ) if 'sluttdato' in x else datetime.strptime( '9999-12-31', '%Y-%m-%d') )
veger = veger[ veger['d1'] <= datetime( 2020, 12, 31 ) ]
veger = veger[ veger['d2'] >  datetime( 2020, 12, 31 ) ]

# lager sammendrag av kjørefelt - har vi 2-3felts veg eller ikkje? 
veger['kjfelt'] = veger['feltoversikt'].apply( lambda x : finnAntallFelt( x ) ) 

# Lager en geodataframe, så vi kan vise ting i kart 
veger['geometry'] = veger['geometri'].apply( lambda x : wkt.loads( x['wkt'] ))
veger = gpd.GeoDataFrame( veger, geometry='geometry', crs=5973 )  

# Lagrer for kartvisning, men må kna vekk noen datatyper som er inkompatible med .gpkg-format
temp = deepcopy( veger )
temp.drop( columns = ['d1', 'd2', 'kontraktsområder', 'riksvegruter' ], inplace=True)
temp['feltoversikt'] = temp['feltoversikt'].apply( lambda x : '#'.join( [ str(y) for y in x  ] if isinstance( x, list) else '' ))
temp.to_file(  'debugmidtrekkverk.gpkg', layer='alleveger', driver='GPKG'  )

# finner kjørefelt fra vegnettet basert på veglenkeposisjoner 
myGdf['kjfelt'] = ''
for i, row in myGdf.iterrows():
    kjfelt = hentKjfelt( row, veger)
    myGdf.at[i,'kjfelt'] = kjfelt

myGdf.to_file(  'debugmidtrekkverk.gpkg', layer='midtrekkverk', driver='GPKG'  )


# For debugging 
lengde = myGdf.groupby( ['fylke', 'vegkategori', 'nummer', 'kjfelt' ]).agg( {'segmentlengde' : 'sum' } ).astype(int).reset_index()
lengde['Veg'] = lengde['vegkategori'] + 'v' + lengde['nummer'].astype(str)
nyttnavn = 'Lengde midtrekkverk totalt per vegnummer (m)'
lengde.rename( columns={ 'segmentlengde' : nyttnavn }, inplace=True  )
lengde = lengde[['fylke', 'Veg', 'kjfelt', nyttnavn]]

telling = myGdf.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
telling.rename( columns={ 'segmentlengde' : 'Lengde midtrekkverk totalt (m)' }, inplace=True)

kun23felt = myGdf[ myGdf['kjfelt'] == '2-3felt']
telling2 = kun23felt.groupby( ['fylke' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
telling2.rename( columns={ 'segmentlengde' : 'Lengde midtrekkverk 2-3felt (m)' }, inplace=True)

skrivdataframe.skrivdf2xlsx( [telling2,             telling,               lengde], '../kostraleveranse2021/Kostra 20 - Midtrekkverk to og trefelts Fv.xlsx', 
                sheet_name=['Midtrekkverk 2-3felt', 'Alle midtrekkverk', 'Midtrekkverk per vegnummer'], metadata=mittfilter)

tidsbruk = datetime.now() - t0 