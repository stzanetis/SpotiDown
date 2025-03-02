import os, wget, music_tag          # type: ignore
from yt_dlp import YoutubeDL        # type: ignore
from ytmusicapi import YTMusic      # type: ignore
from rich.console import Console    # type: ignore

from utils.song_finder import find_best_song1

console = Console()

# Custom logger class for YoutubeDL
class Logger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

def download_tracks(tracks, output_folder):
    print("")
    console.print(f"Starting to download [bold blue]{len(tracks)}[/bold blue] [bold purple]songs[/bold purple]...")

    for track in tracks:
        # Extract song URLs from Youtube Music
        searchtitle = track["track"]["name"] + " " + track["track"]["artists"][0]["name"]

        search_results_songs = YTMusic().search(searchtitle, filter="songs")[:4]    # [:10] is a limiter to limit results to 10 items, 
        search_results_videos = YTMusic().search(searchtitle, filter="videos")[:4]  # filter="songs" to return only actual songs from Youtube Music
        search_results = search_results_songs + search_results_videos
        
        # Check if the song already exists in the output folder by comparing video IDs
        if os.path.exists(output_folder + "\\" + track["track"]["name"] + ".mp3"):
            console.print(f"[bold cyan3]{track['track']['name']}[/bold cyan3] already exists in the output folder.")
            continue

        #video_ids = find_best_song(track, search_results)
        video_ids = find_best_song1(track, search_results_songs, search_results_videos)
        songurl = "https://www.youtube.com/watch?v=" + video_ids['videoId']

        # Downloader options
        name = track["track"]["name"].translate(str.maketrans("", "", '?<>:"/\\|*'))
        ydl_opts = {
            'ffmpeg_location': os.getcwd() + "\\ffmpeg\\bin\\ffmpeg.exe",
            'format': 'bestaudio',
            'outtmpl': output_folder + "\\" + name + ".%(ext)s",
            'noplaylist': True,
            'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            'quiet': True,
            'logger': Logger()
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(songurl)
                insert_metadata(track, output_folder)
        except Exception:
            pass

# Add metadata to the downloaded songs
def insert_metadata(track, output_folder):
    mp3name = track["track"]["name"].translate(str.maketrans("", "", '?<>:"/\\|*'))

    # Create a temp folder if it doesn't exist
    temp_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    if not (os.path.exists(temp_folder) and os.path.isdir(temp_folder)):
        os.mkdir(temp_folder)
    
    # Download necessary metadata
    img = track["track"]["album"]["images"][0]["url"]
    name = track["track"]["name"].translate(str.maketrans("", "", '?<>:"/\\|*'))
    temp_img_path = os.path.join(temp_folder, f"{name}.jpg")
    if not os.path.exists(temp_img_path):
        wget.download(img, out=temp_img_path, bar=None)

    # Add metadata to the downloaded song
    mp3_path = os.path.join(output_folder, f"{mp3name}.mp3")
    f = music_tag.load_file(mp3_path)

    # Add metadata
    f['title'] = name
    f['artist'] = track["track"]["artists"][0]["name"]
    f['album'] = track["track"]["album"]["name"]
    f['year'] = track["track"]["album"]["release_date"].split('-')[0]  # Extract year from release date
    f['tracknumber'] = track["track"]["track_number"]
    with open(temp_img_path, 'rb') as img_file:
        f['artwork'] = img_file.read()
    f.save()