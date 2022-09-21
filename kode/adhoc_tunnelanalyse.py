import pandas as pd


import STARTHER
import nvdbapiv3
import skrivdataframe

def finnlengder( row ):
    if np.isnan( row['Lengde, offisiell'] ):
        return row['Sum lengde alle løp']
    else:
        return row['Lengde, offisiell']

sok = nvdbapiv3.nvdbFagdata( 581 )
sok.filter( {'vegsystemreferanse' : 'Fv' } )
tun = pd.DataFrame( sok.to_records())

# Mangler offisiell lengde, men det viser seg at de har verdi for "sum samlet lengde"
# tun[ tun['Lengde, offisiell'].isnull()][['Navn', 'Lengde, offisiell', 'Sum lengde alle løp', 'Antall parallelle hovedløp']]

tun['Lengde'] = tun.apply( finnlengder, axis=1)

undersjoisk = tun[ tun['Undersjøisk'] == 'Ja'].groupby( 'fylke' ).agg( { 'Lengde' : 'sum' } ).reset_index()
landtunnel = tun[ tun['Undersjøisk'] != 'Ja'].groupby( 'fylke' ).agg( { 'Lengde' : 'sum' } ).reset_index()

undersjoisk.rename( columns={ 'Lengde' : 'Lengde undersjøiske' }, inplace=True )
landtunnel.rename( columns={ 'Lengde' : 'Lengde landtunnel' }, inplace=True )

tunnelltall = pd.merge( landtunnel, undersjoisk, on='fylke', how='left' )
skrivdataframe.skrivdf2xlsx( tunnelltall, 'tunneltall.xlsx' )