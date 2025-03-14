import spotipy, dotenv, os                                              # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth       # type: ignore
from rich.console import Console                                        # type: ignore
from rich.columns import Columns                                        # type: ignore
from rich.prompt import Prompt                                          # type: ignore

console = Console()

# Load Spotify API credentials from .env file
def load_cred():
    dotenv.load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    REDIRECT_URI="https://127.0.0.1:8888/callback"

    return CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# Authenticate and create sp spotify session object
def authenticate_spotify():
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI = load_cred()
    
    console.print("Login to your [bold green]Spotify[/bold green] account through your browser to continue: ", end="")
    #client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-library-read playlist-read-private"))
    console.print("[bold blue]Succesful Login![/bold blue]")
    
    return sp

# List user's playlists and return selection
def select_playlist(sp):
    # Format playlists list
    playlists = sp.current_user_playlists()
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

                if len(items) < 50: # Stop when there are no more songs to fetch
                    break
                offset = offset + 50

                return all_tracks, "Liked Songs"
        else:
            try:
                selected_index = int(userinput) - 1  # Adjust index to match 0-based indexing
                selected_playlist = playlists['items'][selected_index]['name']
                console.print(f"You selected playlist: [bold green]{selected_playlist}[/bold green]")

                playlist_uri = playlists['items'][selected_index]['uri']
                    
                return sp.playlist_tracks(playlist_uri)["items"], selected_playlist
            except (ValueError, IndexError):
                console.print("[bold red]Invalid input[/bold red]. Please enter a [bold green]valid[/bold green] playlist number.")
