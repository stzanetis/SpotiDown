import os, dotenv, spotipy, wget
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL

# Print users playlists and return the songs from the selected playlist
def selectPlaylist(playlists):
    print("   0) Liked Songs")
    for i, playlist in enumerate(playlists['items']):
            print("%4d) %s" % (i+1, playlist['name']))

    while playlists:        
        userinput = input("Enter the number of the playlist you want to select: ")
        if userinput  == "0":
            all_tracks = []
            offset = 0
            while True:
                # Fetch 50 songs at a time
                batch = sp.current_user_saved_tracks(limit=50, offset=offset)
                items = batch['items']
                all_tracks.extend(items)
                # Stop when there are no more songs to fetch
                if len(items) < 50:
                    break
                offset = offset + 50
            return all_tracks
        else:
            try:
                selected_index = int(userinput) - 1  # Adjust index to match 0-based indexing
                selected_playlist = playlists['items'][selected_index]['name']
                print("You selected playlist:", selected_playlist)
                playlist_uri = playlists['items'][selected_index]['uri']
                return sp.playlist_tracks(playlist_uri)["items"]
            except (ValueError, IndexError):
                print("Invalid input. Please enter a valid playlist number.")

        """
        #I don't know what this is..
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
        """

# Search Youtube for the selected songs and download them
def downloadTracks(tracks):
    print("Starting to download %d song(s).." % (len(tracks)))
    error_counter = 0
    for track in tracks:
        # Extract song URLs from Youtube Music
        searchtitle = track["track"]["name"] + " " + track["track"]["artists"][0]["name"] + " (Audio)"
        search_results = YTMusic().search(searchtitle)[:1] # [:1] is a limiter to limit results to 1 item only, filter="songs" to return only actual songs from Youtube Music
        video_ids = [item["videoId"] for item in search_results if "videoId" in item]
        if video_ids == []:
            error_counter = error_counter + 1
            continue
        if video_ids[0] == None:
            search_results = YTMusic().search(searchtitle, filter="songs")[:1]
            video_ids = [item["videoId"] for item in search_results if "videoId" in item]
        songurl = "https://www.youtube.com/watch?v=" + video_ids[0]

        # Create output path
        output_folder = os.getcwd() + "\\bin"
        if not (os.path.exists(output_folder) and os.path.isdir(output_folder)):
            os.mkdir(output_folder)
        
        # Downloader options
        ydl_opts = {
            'ffmpeg_location': os.getcwd() + "\\ffmpeg\\bin\\ffmpeg.exe",
            'format': 'bestaudio',
            'outtmpl': output_folder + "\\%(artist)s - %(title)s.%(ext)s",
            'noplaylist': True,
            'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            'quiet': True,
            'sponsorblock-remove': ['all']
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(songurl)
        except Exception:
            error_counter = error_counter + 1
        #insertMetadata(track)
    print("Downloading Proccess Complete. %d song(s) failed to download." % (error_counter))

# Add metadata to the downloaded songs
def insertMetadata(track):
    print("Downloading and adding metadata for each song..")
    img = track["track"]["album"]["images"][0]["url"]
    name = track["track"]["name"]
    artist_name = track["track"]["artists"][0]["name"]
    album_name = track["track"]["album"]["name"]
    release_date = track["track"]["album"]["release_date"]
    print("name: %s, img: %s, artist_name: %s, album_name: %s, release_date: %s" % (name, img, artist_name, album_name, release_date))
    #wget.download(img)
    


# Load Spotify API credentials from .env file
dotenv.load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI="http://localhost:8888/callback"

# Authenticate and create sp spotify session object
print("Login to your Spotify account through your browser to continue..")
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-library-read"))
print("Succesful Login!")

tracks = selectPlaylist(sp.current_user_playlists())
downloadTracks(tracks)