import os
import re
import spotipy
from pytube import YouTube
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch
from moviepy.editor import VideoFileClip
# import music-tag

# Libraries that may not be needed
import requests as rq

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

def searchSongs(tracks, cho):
    if cho == '3':
        for track in tracks["items"]:
            name = track["track"]["name"]
            artist = track["track"]["artists"][0]["name"]
            artist_title = artist + " " + name
            videosSearch = VideosSearch(artist_title, limit = 1)
            if videosSearch.result():
                # Access the first result and extract the video URL
                video_url = videosSearch.result()['result'][0]['link']
                yttitle = downloadSongs(video_url)
                mp4Tomp3(artist_title, yttitle)
            else:
                print("No results found.")
    else:
        for track in tracks:
            name = track["track"]["name"]
            artist = track["track"]["artists"][0]["name"]
            artist_title = artist + " " + name
            videosSearch = VideosSearch(artist_title, limit = 1)
            if videosSearch.result():
                # Access the first result and extract the video URL
                video_url = videosSearch.result()['result'][0]['link']
                yttitle = downloadSongs(video_url)
                mp4Tomp3(artist_title, yttitle)
            else:
                print("No results found.")

def downloadSongs(url):
    # Create output path
    output_folder = os.getcwd() + "\\Output"
    if not (os.path.exists(output_folder) and os.path.isdir(output_folder)):
        os.mkdir(output_folder)
    
    # Download songs with pytube
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4').first()
    stream.download(output_folder)
    return yt.title # Return title for converting the mp4 file to an mp3

def mp4Tomp3(songname, yttitle):
    # Define the output path
    output_folder = os.getcwd() + "\\Output"

    # Modified path with removed special characters that got here from the song names
    sanitized_path = re.sub(r'[^\w\s\(\)\&\-\\-_]', '', output_folder + "\\" + yttitle)

    video = VideoFileClip(sanitized_path + ".mp4")
    video.audio.write_audiofile(output_folder + "\\" + songname + ".mp3")

    #os.remove(output_folder + "\\" + yt.title + ".mp4")

# Load api credentials from .env file
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI="http://localhost:8888/callback"

# Ask user for type of login
cho1 = input("1.Find Playlists by username    2.Login to your account    3.Get liked songs(only from login)\nSelect an option: ")
if cho1 == '1':
    # Authenticate and create sp spotify session object
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    try: # Get account username from user
        username = input("Spotify account username: ")
    except (ValueError, IndexError):
        print("Invalid username.")
        exit()

    # Extract the public playlists from spotify    
    playlists = sp.user_playlists(username)
    playlist_uri = printPlaylists(playlists)
    tracks = sp.playlist_tracks(playlist_uri)["items"]

    # Search and download songs
    searchSongs(tracks, cho1)
elif cho1 == '2':
    # Extract the playlists from spotify after succesful login from user
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="playlist-read-private"))
    playlists = sp.current_user_playlists()
    playlist_uri = printPlaylists(playlists)
    tracks = sp.playlist_tracks(playlist_uri)["items"]

    # Search and download songs
    searchSongs(tracks, cho1)
elif cho1 == '3':
    # Extract the liked songs from spotify after succesful login from user
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-library-read"))
    tracks = sp.current_user_saved_tracks(limit=10)

    # Download the songs
    searchSongs(tracks, cho1)