import csv
import os
import re

import requests as rq
import spotipy
from pytube import YouTube
from pytube import Search
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
#from moviepy.editor import *

def printPlaylists(playlists):
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
            return playlist_uri
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid playlist number.")

        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

def downloadSongs(tracks):
    # create output path
    #output_folder = "C:" + os.getcwd() + "\Output\\"
    #os.mkdir(output_folder)

    for track in tracks:
        name = track["track"]["name"]
        artist = track["track"]["artists"][0]["name"]
        artist_title = artist + name
        s = Search(artist_title)
        yt = s.results[0]
        stream = yt.streams.filter(only_audio=True).first()
        stream.download() #add output folder in other cases except KHD
        #video = VideoFileClip("example.mp4")
        #video.audio.write_audiofile("example.mp3")

# load credentials from .env file
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI="http://localhost:8888/callback"

# ask user for type of login
cho1 = input("1.Find Playlists by username    2.Login to your account    3.Get liked songs(only from login)    4.Quit\nSelect an option: ")
if cho1 == '1':
    # authenticate and create sp spotify session object
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # get account username from user
    try:
        username = input("Spotify account username: ")
    except (ValueError, IndexError):
        print("Invalid username.")
        exit()

    playlists = sp.user_playlists(username)
    playlist_uri = printPlaylists(playlists)
    tracks = sp.playlist_tracks(playlist_uri)["items"]
    downloadSongs(tracks)
elif cho1 == '2':
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="playlist-read-private"))
    playlists = sp.current_user_playlists()
    playlist_uri = printPlaylists(playlists)
    tracks = sp.playlist_tracks(playlist_uri)["items"]
    downloadSongs(tracks)
elif cho1 == '3':
    # not using fuction downloadSongs because of different format in current_user_saved_tracks
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-library-read"))
    tracks = sp.current_user_saved_tracks(limit=10)
    for track in tracks["items"]:
        name = track["track"]["name"]
        artist = track["track"]["artists"][0]["name"]
        artist_title = artist + name
        s = Search(artist_title)
        yt = s.results[0]
        stream = yt.streams.filter(only_audio=True).first()
        stream.download() #add output folder in other cases except KHD
elif cho1 == '4':
    exit()