import os, wget, music_tag
from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
from rich.console import Console

from utils.song_finder import find_best_song

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
    error_counter = 0

    for track in tracks:
        # Extract song URLs from Youtube Music
        searchtitle = track["track"]["name"] + " " + track["track"]["artists"][0]["name"] + " (Audio)"

        search_results_songs = YTMusic().search(searchtitle, filter="songs")[:4]    # [:10] is a limiter to limit results to 10 items, 
        search_results_videos = YTMusic().search(searchtitle, filter="videos")[:4]  # filter="songs" to return only actual songs from Youtube Music
        search_results = search_results_songs + search_results_videos

        video_ids = find_best_song(track, search_results)

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
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(songurl)
                info_dict = ydl.extract_info(songurl, download=False)
                filename = ydl.prepare_filename(info_dict)
                if filename.endswith(".webm"):
                    filename = filename.replace(".webm", "")
                insert_metadata(track, filename)
        except Exception:
            error_counter = error_counter + 1

# Add metadata to the downloaded songs
def insert_metadata(track, mp3name):
    temp_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    if not (os.path.exists(temp_folder) and os.path.isdir(temp_folder)):
        os.mkdir(temp_folder)
    
    # Download necessary metadata
    img = track["track"]["album"]["images"][0]["url"]
    name = track["track"]["name"]
    artist_name = track["track"]["artists"][0]["name"]
    album_name = track["track"]["album"]["name"]
    release_date = track["track"]["album"]["release_date"]
    wget.download(img, out=os.path.join(temp_folder, f"{name}.jpg"))

    # Add metadata to the downloaded song
    mp3_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", f"{mp3name}.mp3")
    temp_img_path = os.path.join(temp_folder, f"{name}.jpg")

    # Load the mp3 file
    f = music_tag.load_file(mp3_path)

    # Add metadata
    f['title'] = name
    f['artist'] = artist_name
    f['album'] = album_name
    f['year'] = release_date
    f['artwork'] = open(temp_img_path, 'rb').read()
    f.save()

    # Rename the mp3 file to the name of the song
    new_mp3_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", f"{name}.mp3")
    os.rename(mp3_path, new_mp3_path)

    # Replace original file with the new one
    os.replace(f"{mp3_path}.temp", mp3_path)