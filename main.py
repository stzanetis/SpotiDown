# VERSION 1.1

import os, signal
from rich.console import Console

from utils.spotify import authenticate_spotify, select_playlist
from utils.handlers import signal_handler
from utils.downloader import download_tracks
from utils.playlist import generate_playlist

logo = """                                                                                     
   _ _ _     _                      _          _____         _   _ ____                
  | | | |___| |___ ___ _____ ___   | |_ ___   |   __|___ ___| |_|_|    \\ ___ _ _ _ ___ 
  | | | | -_| |  _| . |     | -_|  |  _| . |  |__   | . | . |  _| |  |  | . | | | |   |
  |_____|___|_|___|___|_|_|_|___|  |_| |___|  |_____|  _|___|_| |_|____/|___|_____|_|_|
                                                    |_|                                                                                                        
"""

console = Console()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    console.print(logo, style="bold green")

    # Authenticate and create sp spotify session object
    sp = authenticate_spotify()

    # Create output folder if it doesn't exist
    output_folder = os.path.join(os.path.dirname(__file__), "output")
    if not (os.path.exists(output_folder) and os.path.isdir(output_folder)):
        os.mkdir(output_folder)

    while True:
        # Select playlist
        tracks, playlist_name = select_playlist(sp)

        # Download tracks
        download_tracks(tracks, output_folder)

        # Generate a playlist file to store downloaded playlist songs
        generate_playlist(tracks, playlist_name)

        # Delete temp folder if it exists
        try:
            temp_folder = os.path.join(os.path.dirname(__file__), "temp")
            if os.path.exists(temp_folder) and os.path.isdir(temp_folder):
                for root, dirs, files in os.walk(temp_folder, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(temp_folder)
        except Exception as e:
            console.print(f"\n[bold red]Error deleting temp folder[/bold red]")

        console.print("[bold green]All done! Enjoy your music![/bold green]\n")

if __name__ == "__main__":
    main()