from re import sub
import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER 
import nvdbapiv3
import skrivdataframe 

if __name__ == '__main__': 


    sok = nvdbapiv3.nvdbFagdata(60)
    sok.filter( {'vegsystemreferanse' : 'Fv' } )                    # Fylkesveg  fase V = eksisterende  
    sok.filter( { 'egenskap' : '(1263=7307)'} )                     # Brukategori=Ferjeleie 
    mydf = pd.DataFrame( sok.to_records( vegsegmenter=True ))       # Laster inn i DataFrame (regneark på steroider)
    mydf.drop_duplicates( subset='nvdbId')                          # Tilsvarer punktet i oppskriften om å filtrere med filtreringshjelp=1 

    # print( "Mulige byggverkstyper for bruene vi fant av brukategori=Ferjekai") # Sånn i tilfelle du lurte på det... 
    # print( list( mydf['Byggverkstype'].unique() ))

    # Disse brutypene er definert i oppskriften: 810, 811, 812, 820, 822, 823, 824. Merk at vi hopper over 821. 
    disseByggverkTypene = ['Ferjekaibru (810)', 'Ferjekaibru (811)', 'Ferjekaibru (812)', 'Kai (820)', 'Tilleggskai (822)',  'Tilleggskai (823)', 'Tilleggskai (824)' ]
    # Andre varianter av Byggverkstype jeg finner  i dataene, men som ikke er med i oppskriften 
    #  ['Tilleggskai (821)', 'Ferjekaibru (819)',   'Liggekai (826)', 'Ro-Ro-rampe (828)', 'Liggekai (827)', 
    # 'Kai/bev.bru (800)', 'Reservebru (881)',  'Reservekaibru (813)', 'Andre (890)', 'Molo (831)', 'Ferjekaibru (81)']

    mydf = mydf[ mydf['Byggverkstype'].isin( disseByggverkTypene )].copy() # Filtrerer slik som i oppskriften 
    mydf['antall'] = 1 # Legger til ny kolonne med dataverdi = 1, slik at det blir enklere å telle (aggregere)
    byggverkstype = mydf[['fylke', 'Byggverkstype', 'antall']].pivot_table(  index='fylke', columns='Byggverkstype', aggfunc='count', fill_value=0 )

    # Litt dataframe-wodoo for å få vekk multilevel-kolonnenavn https://stackoverflow.com/a/44023799
    byggverkstype.columns = byggverkstype.columns.droplevel(0)

    # Legger til summeringskolonne 
    byggverkstype['Grand total'] =  byggverkstype.sum(axis='columns')

    if list( byggverkstype.index ) ==  [11, 15, 18, 30, 34, 42, 46, 50, 54]: # Vi har med alle fylkene
        byggverkstype.reindex(         [30, 34, 38, 42, 11, 46, 15, 50, 18] ) # Da kan vi trygt bytte om  på rekkefølgen 

    byggverkstype.reset_index( inplace=True ) # Får fylkesnummer som egen kolonne. Viktig at dette gjøres ETTER kolonnesummeringen (og evt bytting av rekkefølge)

    skrivdataframe.skrivdf2xlsx( byggverkstype, 'Ferjekaibruer.xlsx' )