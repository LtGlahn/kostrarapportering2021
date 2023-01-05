from datetime import datetime 

import geopandas as gpd 

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbgeotricks
import nvdbapiv3

t0 = datetime.now()

mittfilter = { 'tidspunkt'              : '2021-12-16', 
                'trafikantgruppe'       : 'G', 
                'detaljniva'            : 'VT,VTKB',
                'adskiltelop'           : 'med,nei',
                'historisk'             : 'true', 
                'vegsystemreferanse'    : 'Fv',
                'veglenketype'          : 'hoved', 
                'typeveg'               : 'kanalisertVeg,enkelBilveg,rampe,rundkjøring,gangOgSykkelveg,sykkelveg,gangveg,gatetun'
                }


# Hm, kan ikke ha med alle de snåle filtrene! 

myGdf = nvdbgeotricks.vegnett2gdf( mittfilter=mittfilter )

statistikk = myGdf.groupby( ['fylke'] ).agg( { 'lengde' : 'sum' } ).reset_index()

skrivdataframe.skrivdf2xlsx( statistikk, '../kostraleveranse2021/Kostra 21 gang og sykkelveg.xlsx', 
    sheet_name='Fylkesveg gang og sykkelveg', metadata=mittfilter)


myGdf.to_file( 'sykkelveg.gpkg', layer='gangsykkelveg', driver='GPKG')

tidsbruk = datetime.now() - t0 