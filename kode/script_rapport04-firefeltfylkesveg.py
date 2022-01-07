
"""
Last ned med disse valgene: 
https://raw.githubusercontent.com/LtGlahn/kostrarapportering2021/master/bilder/lastned04-firefeltsfylkesveg.png

"""


print( "Last ned fra https://nvdb-kostra.atlas.vegvesen.no/ med valgene")
print( "https://raw.githubusercontent.com/LtGlahn/kostrarapportering2021/master/bilder/lastned04-firefeltsfylkesveg.png")

# ALternativ - bygg videre på kode som er brukt til å verifisere resultatet 
# from datetime import date, datetime 

# import geopandas as gpd 
# import pandas as pd
# import numpy as np
# from copy import deepcopy

# import STARTHER
# import lastnedvegnett  
# import skrivdataframe
# import nvdbapiv3
# import nvdbgeotricks


# t0 = datetime.now()

# mittfilter = lastnedvegnett.filtersjekk()
# mittfilter['vegsystemreferanse'] = 'Fv'
# mittfilter['typeveg'] =  'kanalisertVeg,enkelBilveg'
# junk = mittfilter.pop( 'historisk', None )

# firefelt = nvdbgeotricks.firefeltrapport( mittfilter=mittfilter, felttype='firefelt')
# telling = firefelt.groupby( ['fylke' ]).agg( {'lengde' : 'sum' } )  
