
"""
Ad-hoc firefelt-rapportering på europa-og riksveg. Kopi av (klone av) `script_rapport04-firefeltfylkesveg.py` 
"""

from datetime import date, datetime 

import geopandas as gpd 
import pandas as pd
import numpy as np
from copy import deepcopy

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3
import nvdbgeotricks


t0 = datetime.now()

mittfilter = lastnedvegnett.filtersjekk()
mittfilter['vegsystemreferanse'] = 'Ev,Rv'
mittfilter['typeveg'] =  'kanalisertVeg,enkelBilveg'
junk = mittfilter.pop( 'historisk', None )

firefelt = nvdbgeotricks.firefeltrapport( mittfilter=mittfilter, felttype='firefelt')
telling = firefelt.groupby( ['fylke' ]).agg( {'lengde' : 'sum' } )  

print( f"Antall km firefelt på europa- og riksveg per {mittfilter['tidspunkt']}: {round( firefelt['lengde'].sum()/1000)}km " )