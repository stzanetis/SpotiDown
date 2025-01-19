# SpotiDown

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

## Important

- Right now you can only use this by creating your own app in spotify web developer and putting your client id and secret to a .env file.
- Binaries for ffmpeg also need to be in the repository directory in order to convert the webm files downloaded from ytdlp to mp3 files.
