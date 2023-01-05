from re import sub
import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER 
import nvdbapiv3
import skrivdataframe 


if __name__ == '__main__': 

    gpkgfil = 'drift-statsbudsjettEogRveger.gpkg'
    #  Henter vegnett 
    sok = nvdbapiv3.nvdbVegnett( )
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv', 'trafikantgruppe' : 'K'}
    sok.filter( mittfilter )
    veg = pd.DataFrame( sok.to_records() )
    veg = veg[ veg['adskilte_lop'] != 'Mot']
    veg = veg[ veg['type'] == 'HOVED'].copy()

    # Tar vekk sideanlegg 
    veg = veg[  veg['sideanleggsdel'].isnull() ]

    # Tar vekk kryssdeler som ikke er rundkjøringer  
    veg = veg[ (veg['kryssdel'].isnull() ) | (veg['typeVeg'] == 'Rundkjøring') ]

    # Tar vekk de tre irriterende gangstiene som har trafikantgruppe K
    veg = veg[ veg['typeVeg'] != 'Gang- og sykkelveg'].copy()

    veg['geometry'] = veg['geometri'].apply( wkt.loads )
    veg = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )

    vegcol = ['veglenkesekvensid',  'startposisjon', 'sluttposisjon', 'type', 'detaljnivå', 'typeVeg',
                 'feltoversikt', 'geometri', 'lengde', 'fylke', 'kommune', 'startdato', 'vref', 'vegkategori',
                 'fase', 'nummer', 'adskilte_lop', 'medium', 'topologinivå', 'geometry']

    lengde_veg_KM = veg['lengde'].sum() / 1000
    veg[vegcol].to_file( gpkgfil, layer='ERvegnett', driver='GPKG')

    # # Henter TEN-T veg 
    sok = nvdbapiv3.nvdbFagdata( 826 )
    sok.filter( mittfilter  )
    tent = pd.DataFrame( sok.to_records( ))

    tent = tent[ tent['adskilte_lop'] != 'Mot'  ]

    # Filtrerer sideanlegg
    tent = tent[ ~tent['vref'].str.contains('SD')]

    # Filtrerer vekk kryssdeler som ikke er rundkjøringer
    tent = tent[ ( ~tent['vref'].str.contains('KD')) | (tent['typeVeg'] == 'Rundkjøring' ) ]

    tent['geometry'] = tent['geometri'].apply( wkt.loads )
    tent = gpd.GeoDataFrame( tent, geometry='geometry', crs=5973 )
    tent.to_file( gpkgfil, layer='tent', driver='GPKG')

    lengde_tent_KM = tent['segmentlengde'].sum( ) / 1000 

    # Henter motorveg 
    sok = nvdbapiv3.nvdbFagdata( 595 )
    sok.filter( mittfilter )
    motor = pd.DataFrame( sok.to_records( ))

    motor = motor[ motor['adskilte_lop'] != 'Mot'  ]

    # Filtrerer sideanlegg
    motor = motor[ ~motor['vref'].str.contains('SD')]

    # Filtrerer vekk kryssdeler som ikke er rundkjøringer
    motor = motor[ ( ~motor['vref'].str.contains('KD')) | (motor['typeVeg'] == 'Rundkjøring' ) ]

    motor['geometry'] = motor['geometri'].apply( wkt.loads )
    motor = gpd.GeoDataFrame( motor, geometry='geometry', crs=5973 )
    motor.to_file( gpkgfil, layer='motorveg', driver='GPKG')

    lengde_motorveg_KM = motor[ motor['Motorvegtype'] == 'Motorveg'] ['segmentlengde'].sum( ) / 1000 
    lengde_motortrafikkveg_KM = motor[ motor['Motorvegtype'] == 'Motortrafikkveg'] ['segmentlengde'].sum( ) / 1000 

    print( f"Lengde E+R vegnett {round( lengde_veg_KM )} km ")
    print( f"Lengde TEN-T vegnett {round( lengde_tent_KM )} km ")
    print( f"Lengde Motorvegtype=Motorveg {round( lengde_motorveg_KM )} km ")
    print( f"Lengde Motorvegtype=Motorveg {round( lengde_motortrafikkveg_KM )} km ")

