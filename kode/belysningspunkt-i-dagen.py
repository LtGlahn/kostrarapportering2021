import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3
import skrivdataframe



sok = nvdbapiv3.nvdbFagdata( 87 )
sok.filter( {'vegsystemreferanse' : 'Fv' } )

alleBelPunkt = pd.DataFrame( sok.to_records())

# GRRR, denne oppskriften funker ikke, overlapp funker kun UTEN andre typer filter! 
sok = nvdbapiv3.nvdbFagdata( 87 )
sok.filter( {'vegsystemreferanse' : 'Fv' } )
sok.filter( { 'overlapp' : '67' } )
itunnell = pd.DataFrame( sok.to_records())


# Lagrer til fil for debugging
itunnell['geometry'] = itunnell['geometri'].apply( wkt.loads )
itunnel = gpd.GeoDataFrame( itunnell, geometry='geometry', crs=5973 )
itunnel.to_file( 'belysningspunkt.gpkg', layer='Fv_overlapp67', driver='GPKG' )

alleBelPunkt['geometry'] = alleBelPunkt['geometri'].apply( wkt.loads)
alleBelPunkt = gpd.GeoDataFrame( alleBelPunkt, geometry='geometry', crs=5973 )
alleBelPunkt.to_file( 'belysningspunkt.gpkg', layer='allebelpunkt', driver='GPKG' )


# Tar ut ALLE data, sorterer etterpå 
sok = nvdbapiv3.nvdbFagdata( 87 )
sok.filter( { 'overlapp' : '67' } )


itunnel = pd.DataFrame( sok.to_records())
utafor = alleBelPunkt[ ~alleBelPunkt['nvdbId'].isin(  itunnel['nvdbId'].to_list() ) ]
# len( alleBelPunkt) - len( utafor)
sammendrag = utafor.groupby( 'fylke' ).agg( {'nvdbId' : 'count' }).reset_index()

skrivdataframe.skrivdf2xlsx( sammendrag, 'belysningspunktUtaforTunnel.xlsx' )