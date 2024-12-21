import os, dotenv, spotipy, wget, music_tag, signal, time           # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth   # type: ignore
from ytmusicapi import YTMusic                                      # type: ignore
from yt_dlp import YoutubeDL                                        # type: ignore

# Rich library imports for console output
from rich.console import Console                                    # type: ignore
from rich.columns import Columns                                    # type: ignore
from rich.prompt import Prompt                                      # type: ignore
from rich.progress import Progress                                  # type: ignore

logo = """                                                                                     
   _ _ _     _                      _          _____         _   _ ____                
  | | | |___| |___ ___ _____ ___   | |_ ___   |   __|___ ___| |_|_|    \ ___ _ _ _ ___ 
  | | | | -_| |  _| . |     | -_|  |  _| . |  |__   | . | . |  _| |  |  | . | | | |   |
  |_____|___|_|___|___|_|_|_|___|  |_| |___|  |_____|  _|___|_| |_|____/|___|_____|_|_|
                                                    |_|                                                                                                        
"""

# Custom logger class for YoutubeDL
class Logger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

# Print users playlists and return the songs from the selected playlist
def selectPlaylist(playlists):
    # Display all availabel options
    playlist_names = ["Liked Songs"] + [playlist['name'] for playlist in playlists['items']]                    # Add "Liked Songs" as the first item
    numbered_playlists = [f"[bold blue]{i}.[/bold blue] {name}" for i, name in enumerate(playlist_names)]       # Create a list of numbered playlists
    formatted_columns = ["\n".join(numbered_playlists[i:i + 4]) for i in range(0, len(numbered_playlists), 4)]  # Format into 3 items per column

    console.print("[bold green]Available Playlists:[/bold green]")
    console.print(Columns(formatted_columns, expand=True))

    while playlists:
        userinput = Prompt.ask("Enter the number of the playlist you want to select")     
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
                console.print(f"You selected playlist: [bold green]{selected_playlist}[/bold green]")
                playlist_uri = playlists['items'][selected_index]['uri']
                return sp.playlist_tracks(playlist_uri)["items"]
            except (ValueError, IndexError):
                console.print("[bold red]Invalid input[/bold red]. Please enter a [bold green]valid[/bold green] playlist number.")

# Search Youtube for the selected songs and download them
def downloadTracks(tracks):
    print("")
    console.print(f"Starting to download [bold blue]{len(tracks)}[/bold blue] [bold purple]songs[/bold purple]...")
    error_counter = 0

    # Create output folder if it doesn't exist
    output_folder = os.getcwd() + "\\output"
    if not (os.path.exists(output_folder) and os.path.isdir(output_folder)):
        os.mkdir(output_folder)

    for track in tracks:
        # Extract song URLs from Youtube Music
        searchtitle = track["track"]["name"] + " " + track["track"]["artists"][0]["name"] + " (Audio)"

        search_results_songs = YTMusic().search(searchtitle, filter="songs")[:4]    # [:10] is a limiter to limit results to 10 items, 
        search_results_videos = YTMusic().search(searchtitle, filter="videos")[:4]  # filter="songs" to return only actual songs from Youtube Music
        search_results = search_results_songs + search_results_videos

        video_ids = findBestSong(track, search_results)     

        if video_ids == []:
            error_counter = error_counter + 1
            continue
        songurl = "https://www.youtube.com/watch?v=" + video_ids['videoId']
        
        # Check if the song already exists in the output folder by comparing video IDs
        if os.path.exists(output_folder + "\\" + track["track"]["name"] + ".mp3"):
            print("Song already exists in the output folder. Skipping..")
            continue

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
            'logger': Logger(),
            'sponsorblock-remove': ['all'],
        }
        try:
            #print("Downloading: %s" % (track["track"]["name"]))
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(songurl)
                info_dict = ydl.extract_info(songurl, download=False)
                filename = ydl.prepare_filename(info_dict)
                if filename.endswith(".webm"):
                    filename = filename.replace(".webm", "")
                insertMetadata(track, filename)
        except Exception:
            error_counter = error_counter + 1

    console.print()
    return error_counter

# Add metadata to the downloaded songs
def insertMetadata(track, mp3name):
    # Create temp folder if it doesn't exist
    temp_folder = os.getcwd() + "\\temp"
    if not (os.path.exists(temp_folder) and os.path.isdir(temp_folder)):
        os.mkdir(temp_folder)
    
    # Download necessary metadata
    #print("Downloading and adding metadata to: %s" % (track["track"]["name"]))
    img = track["track"]["album"]["images"][0]["url"]
    name = track["track"]["name"]
    artist_name = track["track"]["artists"][0]["name"]
    album_name = track["track"]["album"]["name"]
    release_date = track["track"]["album"]["release_date"]
    wget.download(img, out=os.path.join(temp_folder, f"{name}.jpg"))

    # Add metadata to the downloaded song
    mp3_path = os.path.join(os.getcwd(), "output", f"{mp3name}.mp3")
    temp_img_path = os.path.join(temp_folder, f"{name}.jpg")

    # Load the mp3 file
    f = music_tag.load_file(mp3_path)

    # Add metadata
    f['title'] = name
    f['artist'] = artist_name
    f['album'] = album_name
    f['year'] = release_date
    f['artwork'] = open(temp_img_path, 'rb').read()

    # Save changes
    f.save()

    # Rename the mp3 file to the name of the song
    new_mp3_path = os.path.join(os.getcwd(), "output", f"{name}.mp3")
    os.rename(mp3_path, new_mp3_path)

    # Replace original file with the new one
    os.replace(f"{mp3_path}.temp", mp3_path)
    #print(f"Metadata added and saved to {mp3_path}")

# Find the best matching song from the search results
def findBestSong(track, search_results):
    best_score = 0
    best_match = None

    w_name, w_artist, w_duration = 0.5, 0.3, 0.2
    spotify_name = track["track"]["name"].lower()
    spotify_artist = track["track"]["artists"][0]["name"].lower()
    spotify_duration = track["track"]["duration_ms"] / 1000
    for result in search_results:
        #print("Spotify name: %s, Spotify artist: %s, Spotify duration: %d" % (spotify_name, spotify_artist, spotify_duration))
        #print("Youtube name: %s, Youtube artist: %s, Youtube duration: %d" % (result["title"].lower(), result["artists"][0]["name"].lower(), result["duration_seconds"]))
        youtube_name = result["title"].lower()
        youtube_artist = result["artists"][0]["name"].lower()
        youtube_duration = result["duration_seconds"]

        name_match = sum(1 for char in spotify_name if char in youtube_name) / len(spotify_name)
        artist_match = sum(1 for artist in spotify_artist if artist in youtube_artist) / len(spotify_artist)
        duration_match = 1 - min(1, abs(spotify_duration - youtube_duration) / spotify_duration * 0.1)
        score = (w_artist * artist_match +
                 w_name * name_match +
                 w_duration * duration_match)
        #print("Score: %f" % (score))
        if score > best_score:
            best_score = score
            best_match = result
    return best_match

# Signal handler for keyboard interrupt
def signal_handler(sig, frame):
    console.print("\n[bold red]Process terminated by user. Exiting...[/bold red]")
    exit(0)

# Main program
signal.signal(signal.SIGINT, signal_handler)
console = Console()
console.print(logo, style="bold green")

# Load Spotify API credentials from .env file
dotenv.load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI="http://localhost:8888/callback"

# Authenticate and create sp spotify session object
console.print("Login to your [bold green]Spotify[/bold green] account through your browser to continue: ", end="")
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-library-read playlist-read-private"))
console.print("[bold blue]Succesful Login![/bold blue]")

# Select playlist and download songs
tracks = selectPlaylist(sp.current_user_playlists())
errors = downloadTracks(tracks)

print("")
if errors > 0:
    console.print(f"[bold red]{errors} songs could not be downloaded.[/bold red]")
console.print("[bold green]All done! Enjoy your music![/bold green]")