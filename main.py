# VERSION 1.2.1

import os, signal, argparse
from rich.console import Console
from rich.prompt import Prompt

from utils.spotify import authenticate_spotify, select_playlist
from utils.handlers import signal_handler
from utils.downloader import download_tracks
from utils.playlist import generate_m3u_playlist, generate_xspf_playlist, generate_pls_playlist

logo = """                                                                                     
   _ _ _     _                      _          _____         _   _ ____                
  | | | |___| |___ ___ _____ ___   | |_ ___   |   __|___ ___| |_|_|    \\ ___ _ _ _ ___ 
  | | | | -_| |  _| . |     | -_|  |  _| . |  |__   | . | . |  _| |  |  | . | | | |   |
  |_____|___|_|___|___|_|_|_|___|  |_| |___|  |_____|  _|___|_| |_|____/|___|_____|_|_|
                                                    |_|                                                                                                        
"""

console = Console()

def playlist_gen(format, songs, output_folder, playlist_name):
    if format == "m3u":
        generate_m3u_playlist(songs, output_folder, playlist_name)
    elif format == "xspf":
        generate_xspf_playlist(songs, output_folder, playlist_name)
    elif format == "pls":
        generate_pls_playlist(songs, output_folder, playlist_name)
    else:
        console.print("[bold red]Invalid playlist format. Defaulting to m3u format[/bold red]")
        generate_m3u_playlist(songs, output_folder, playlist_name)

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Github Page: https://github.com/stzanetis/SpotiDown")
    parser.add_argument(
        "-v", "--version", action="version",
        version="SpotiDown v1.1", help="Shows program version"
    )
    parser.add_argument(
        "-o", "--output",
        type=str, default = os.path.join(os.path.dirname(__file__), "output"),
        metavar="",
        help="Specify the output directory to store tracks"
    )
    parser.add_argument(
        "-l", "--link",
        type=str, default=None,
        metavar="",
        help="Specify a particular track link to download"
    )
    parser.add_argument(
        "-p", "--playlist",
        type=str, default=None,
        metavar="",
        help="Specify a particular playlist link to download"
    )
    parser.add_argument(
        "-f", "--format",
        type=str, default="m3u",
        metavar="",
        help="Specify the playlist format to generate (m3u, xspf, pls)"
    )
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    console.print(logo, style="bold green")

    # Authenticate and create sp spotify session object
    sp = authenticate_spotify()

    # Create output folder if it doesn't exist
    output_folder = args.output
    if not (os.path.exists(output_folder) and os.path.isdir(output_folder)):
        os.mkdir(output_folder)

    # Create playlist folder if it doesn't exist
    playlist_folder = os.path.join(output_folder, "Playlists")
    if not (os.path.exists(playlist_folder) and os.path.isdir(playlist_folder)):
        os.mkdir(playlist_folder)

    if args.playlist:
        playlist_id = args.playlist.split("/")[-1].split("?")[0]  # Extract playlist ID
        playlist_tracks = sp.playlist_tracks(playlist_id)
        songs = []
        for item in playlist_tracks['items']:
            track = item['track']
            songs.append({"track": track})
        download_tracks(songs, output_folder)

        # Generate playlist file
        playlist_gen(args.format, songs, output_folder, sp.playlist(playlist_id)['name'])
        console.print("[bold green]All done! Enjoy your music![/bold green]\n")
        return
    elif args.link:
        track = sp.track(args.link)
        download_tracks([{"track": track}], output_folder)
        console.print("[bold green]All done! Enjoy your music![/bold green]\n")
        return

    while True:
        # Select playlist
        tracks, playlist_name = select_playlist(sp)

        # Download tracks
        download_tracks(tracks, output_folder)

        # Generate a playlist file 
        playlist_gen(args.format, tracks, output_folder, playlist_name) 

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