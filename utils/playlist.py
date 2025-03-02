import os, re
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def sanitize_filename(filename):
    # Remove or replace invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Generate a m3u playlist
def generate_m3u_playlist(tracks, output_folder, playlist_name):
    sanitized_playlist_name = sanitize_filename(playlist_name)
    playlist_path = os.path.join(output_folder, "Playlists", f"{sanitized_playlist_name}.m3u")

    # Check for any songs that may already exist in the playlist
    existing_songs = []
    if os.path.exists(playlist_path):
        with open(playlist_path, "r", encoding="utf-8") as playlist_file:
            existing_songs = playlist_file.read().splitlines()
 
    playlist_mode = Prompt.ask("Should the playlist be compatible with Windows or Android?", choices=["Windows", "Android"])
    while playlist_mode not in ["Windows", "Android"]:
            console.print("Invalid choice. Please select either 'Windows' or 'Android'.")
    if playlist_mode == "Windows":
        path = output_folder
    elif playlist_mode == "Android":
        path = "/storage/emulated/0/Music"

    # Append new songs to the playlist
    with open(playlist_path, "a", encoding="utf-8") as playlist_file:
        if not existing_songs:
            playlist_file.write("#EXTM3U\n")
        for song in tracks:
            song_name = song["track"]["name"].translate(str.maketrans("", "", '?<>:"/\\|*'))
            song_duration = int(song['track']['duration_ms'] / 1000)
            song_path = os.path.join(path, f"{song_name}.mp3")
            if song_path not in existing_songs:
                metadata = f"#EXTINF:{song_duration},{os.path.basename(song_name)}\n"
                playlist_file.write(metadata)
                playlist_file.write(song_path + "\n")

# Generate XSPF playlist
def generate_xspf_playlist(tracks, output_folder, playlist_name):
    sanitized_playlist_name = sanitize_filename(playlist_name)
    playlist_path = os.path.join(output_folder, "Playlists", f"{sanitized_playlist_name}.xspf")

    playlist_mode = Prompt.ask("Should the playlist be compatible with Windows or Android?", choices=["Windows", "Android"])
    while playlist_mode not in ["Windows", "Android"]:
        console.print("Invalid choice. Please select either 'Windows' or 'Android'.")
    if playlist_mode == "Windows":
        path = output_folder
    elif playlist_mode == "Android":
        path = "/storage/emulated/0/Music"

    with open(playlist_path, "w", encoding="utf-8") as playlist_file:
        playlist_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        playlist_file.write('<playlist version="1" xmlns="http://xspf.org/ns/0/">\n')
        playlist_file.write('  <trackList>\n')
        for song in tracks:
            song_name = song['track']['name']
            song_duration = int(song['track']['duration_ms'] / 1000)
            song_path = os.path.join(path, f"{song_name}.mp3")
            metadata = f'    <track><title>{song_name}</title><location>{song_path}</location><duration>{song_duration}</duration></track>\n'
            playlist_file.write(metadata)
        playlist_file.write('  </trackList>\n')
        playlist_file.write('</playlist>\n')

def generate_pls_playlist(tracks, output_folder, playlist_name):
    sanitized_playlist_name = sanitize_filename(playlist_name)
    playlist_path = os.path.join(output_folder, "Playlists", f"{sanitized_playlist_name}.pls")

    playlist_mode = Prompt.ask("Should the playlist be compatible with Windows or Android?", choices=["Windows", "Android"])
    while playlist_mode not in ["Windows", "Android"]:
        console.print("Invalid choice. Please select either 'Windows' or 'Android'.")
    if playlist_mode == "Windows":
        path = output_folder
    elif playlist_mode == "Android":
        path = "/storage/emulated/0/Music"

    with open(playlist_path, "w", encoding="utf-8") as playlist_file:
        playlist_file.write('[playlist]\n')
        playlist_file.write(f'NumberOfEntries={len(tracks)}\n')
        for index, song in enumerate(tracks):
            song_name = song['track']['name']
            song_duration = int(song['track']['duration_ms'] / 1000)
            song_path = os.path.join(path, f"{song_name}.mp3")
            metadata = f'File{index + 1}={song_path}\n'
            title = f'Title{index + 1}={song_name}\n'
            length = f'Length{index + 1}={song_duration}\n'
            playlist_file.write(metadata)
            playlist_file.write(title)
            playlist_file.write(length)
        playlist_file.write('Version=2\n')