from re import sub
import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER 
import nvdbapiv3
import skrivdataframe 

if __name__ == '__main__': 

    gpkgfil = 'script_belysningspunkt.gpkg'

    sok = nvdbapiv3.nvdbFagdata(87 )
    sok.filter( {'vegsystemreferanse' : 'Fv' } )                    # Fylkesveg  fase V = eksisterende  
    mydf = pd.DataFrame( sok.to_records( vegsegmenter=True ))       # Laster inn i DataFrame (regneark på steroider)

    # Tydeliggjør manglende verdi for Bruksområde og Eier
    mydf['Bruksområde'].fillna( 'IKKE REGISTRERT bruksområde', inplace=True )
    mydf['Eier'].fillna( 'IKKE REGISTRERT Eier', inplace=True )
    
    # Lager geodataframe, så vi kan feilsøke på geografiske data
    mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
    mydf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )
    mydf.to_file( gpkgfil, layer='allebelysningspunkt', driver='GPKG'  )

    # Filtreer i hht oppskrift - Fv filteret har vi allerede gjort i spørringe
    mydf = mydf[ mydf['trafikantgruppe'] == 'K'].copy()

    # Utforsker om vi har hatt problemer med at analysen utelater "IKKE REGISTRERT" Bruksområde eller Eier? 
    bruksFilter1 = [ 'Belysning bru', 'Belysning ferjeleie', 'Belysning gangfelt', 'Belysning område/plass', 'Belysning skilt', 'Belysning veg/gate', 'Belysning vegkryss' ] 
    bruksFilter2 = bruksFilter1 + ['IKKE REGISTRERT bruksområde']

    eierFilter1 =  [ 'Fylkeskommune', 'Stat, Statens vegvesen' ]
    eierFilter2 = eierFilter1 + [ 'IKKE REGISTRERT Eier' ]

    lysBruksfilter1 = mydf[ mydf['Bruksområde'].isin( bruksFilter1 )]
    lysBruksfilter2 = mydf[ mydf['Bruksområde'].isin( bruksFilter2 )]

    # lysBfilter1Eierfilter1 = lysBruksfilter1[ lysBruksfilter1['Eier'].isin( eierFilter1 )]
    # lysBfilter1Eierfilter2 = lysBruksfilter1[ lysBruksfilter1['Eier'].isin( eierFilter2 )]
    # lysBfilter2Eierfilter1 = lysBruksfilter2[ lysBruksfilter2['Eier'].isin( eierFilter1 )]
    lysBfilter2Eierfilter2 = lysBruksfilter2[ lysBruksfilter2['Eier'].isin( eierFilter2 )] # 175434 <= HELT KLART denne varianten vi bruker

    lysBfilter2Eierfilter2.to_file( gpkgfil, layer='filtrertBruksomrEier', driver='GPKG')

    # print( f"Antall lys med bruksområde={','.join(bruksFilter1)} Eier={eierFilter1} : {len(lysBfilter1Eierfilter1)} ") # 78464
    # print( f"Antall lys med bruksområde={','.join(bruksFilter1)} Eier={eierFilter2} : {len(lysBfilter1Eierfilter2)} ") # 158069
    # print( f"Antall lys med bruksområde={','.join(bruksFilter2)} Eier={eierFilter1} : {len(lysBfilter2Eierfilter1)} ") #  81862
    print( f"Antall lys med bruksområde={','.join(bruksFilter2)} Eier={eierFilter2} : {len(lysBfilter2Eierfilter2)} ") # 175434 <= HELT KLART denne varianten vi bruker

    # Til opplysning ang definisjonen "Lyspunkt i dagen"
    # Via søk etter belysningspunkt som overlapper med tunnelløp og filtrering på vegkategori=F, fase=V og trafikantgruppe=K 
    # så får vi 64779 belysningspunkt inne i tunnellen. Det gir oss følgende interessante regnestykke: 
    # 
    # Belysningspunkt på Fv, trafikantgruppe K           293158
    #   - Belysningspunkt som overlapper med tunnelløp  - 64779
    # ---------------------------------------------------------
    # = Belysningspunkt utafor tunnel                    228379
    #
    # Mens med filtrene på Bruksområde + Eier så får vi  175434
    # Altså cirka 52.945 belysningspunkt som ligger utafor tunnelløp, men ikke inkluderes i filtrene våre. 
    #   228379 vs 175434, det har litt betydning når vi snakker statsbudsjett. 


    # antallLys_filter_1_1 = lysBfilter1Eierfilter1.groupby( 'fylke').agg( {'nvdbId' : 'count'}) # Ignorer
    # antallLys_filter_1_2 = lysBfilter1Eierfilter2.groupby( 'fylke').agg( {'nvdbId' : 'count'}) # Ignorer
    # antallLys_filter_2_1 = lysBfilter2Eierfilter1.groupby( 'fylke').agg( {'nvdbId' : 'count'}) # Ignorer
    antallLys_filter_2_2 = lysBfilter2Eierfilter2.groupby( 'fylke').agg( {'nvdbId' : 'count'})   # <= BRUK DENNE 

    if list( antallLys_filter_2_2.index ) ==  [11, 15, 18, 30, 34, 42, 46, 50, 54]: # Vi har med alle fylkene
        antallLys_filter_2_2.reindex(         [30, 34, 38, 42, 11, 46, 15, 50, 18] ) # Da kan vi trygt bytte om  på rekkefølgen 

    antallLys_filter_2_2.reset_index( inplace=True )

    skrivdataframe.skrivdf2xlsx( antallLys_filter_2_2, 'belysningspunkt.xlsx' )

