import csv
import os
import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials(client_id='9f656a5110cf4dcc8738d7b23ccfc1a4', client_secret='299a3998a9d54683b246db53cc37f479')
sp = spotipy.Spotify(auth_manager=auth_manager)

#random numbers are the username
playlists = sp.user_playlists('58i3445p606hfplut8d5dkldo')
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s" % (i + 1 , playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None