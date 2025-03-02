# SpotiDown

![CLI interface](https://drive.google.com/file/d/1G9xHP51C2te_GYy4RZY6s94p3OgShz3V/view)

SpotiDown is a **Python-based** program that downloads your **Spotify** music playlists from YouTube, even **without a premium subscription**. All you need to do is log in with your personal Spotify account, and you can choose to download any of your playlists or favorite songs!

## Features

- Download Spotify *playlists* and *favorite songs*.
- Metadata and album artwork added to songs.
- Create `.m3u` files for importing your playlists as they are on spotify on your favorite offline music player.

## Installation

To get started, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/stzanetis/SpotiDown.git
cd spotidown
pip install -r requirements.txt
python ./main.py
```

## Usage

### Prerequisites

- Create your own app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and add your client ID and secret to a `.env` file
- Ensure FFmpeg binaries are in the repository directory to convert YouTube downloads to MP3 format

### Basic Usage

After successfully logging in, you can select the playlist you want to download from the interactive menu.

### Advanced Options

You can also download specific songs or playlists by passing arguments at execution time:

```bash
# Download a specific playlist using its URL
python main.py --playlist "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"

# Change the output directory
python main.py --output "/path/to/music"

# Specify playlist file format
python main.py --format "m3u8"
```

For a complete list of available arguments:

```bash
python main.py --help
```
