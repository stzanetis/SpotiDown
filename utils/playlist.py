import os, re

def sanitize_filename(filename):
    # Remove or replace invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Generate a m3u playlist based on spotify
def generate_playlist(tracks, playlist_name):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    sanitized_playlist_name = sanitize_filename(playlist_name)
    playlist_path = os.path.join(base_dir, "output", "Playlists", f"{sanitized_playlist_name}.m3u")

    # Check for any songs that may already exist in the playlist
    if os.path.exists(playlist_path):
        with open(playlist_path, "r", encoding="utf-8") as playlist_file:
            existing_songs = playlist_file.read().splitlines()
    else:
        existing_songs = []

    # Append new songs to the playlist
    with open(playlist_path, "a", encoding="utf-8") as playlist_file:
        if not existing_songs:
            playlist_file.write("#EXTM3U\n")
        for song in tracks:
            song_name = song['track']['name']
            song_duration = int(song['track']['duration_ms'] / 1000)
            song_path = "/storage/emulated/0/Music/" + song_name + ".mp3"
            if song_path not in existing_songs:
                metadata = f"#EXTINF:{song_duration},{os.path.basename(song_name)}\n"
                playlist_file.write(metadata)
                playlist_file.write(song_path + "\n")