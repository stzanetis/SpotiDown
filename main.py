import csv
import os
import re

import spotipy
from pytube import YouTube
from pytube import Search
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# load credentials from .env file
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
OUTPUT_FILE_NAME = "track_info.csv"

# authenticate and create sp spotify session object
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

try:
    username = input("Spotify account username: ")
except (ValueError, IndexError):
    print("Invalid username.")
    exit()

playlists = sp.user_playlists(username)
print("Loading playlists..")
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s" % (i+1, playlist['name']))

    user_input = input("Enter the number of the playlist you want to select: ")
    try:
        selected_index = int(user_input) - 1  # Adjust index to match 0-based indexing
        selected_playlist = playlists['items'][selected_index]['name']
        print("You selected playlist:", selected_playlist)
        playlist_uri = playlists['items'][selected_index]['uri']
    except (ValueError, IndexError):
        print("Invalid input. Please enter a valid playlist number.")

    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

# get list of tracks in a given playlist (note: max playlist length 100)
tracks = sp.playlist_tracks(playlist_uri)["items"]
a = len(tracks)
print(a)

# create csv file
with open(OUTPUT_FILE_NAME, "w", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # write header column names
    writer.writerow(["track", "artist"])

    # extract name and artist
    for track in tracks:
        name = track["track"]["name"]
        artists = ", ".join(
            [artist["name"] for artist in track["track"]["artists"]]
        )
        artist_title = artists + name
        s = Search(artist_title)
        yt = s.results[0]
        stream = yt.streams.filter(only_audio=True).first()
        stream.download()

        # write to csv
        writer.writerow([name, artists])