# SpotiDown
SpotiDown is a Python-based program that downloads your Spotify music playlists from YouTube, even without a premium subscription. All you need to do is log in with your personal Spotify account, and you can choose to download any of your playlists or favorite songs!

## Introduction
SpotiDown allows you to download your Spotify playlists directly from YouTube. This tool is perfect for users who want to enjoy their favorite music offline without needing a Spotify premium subscription.

## Features
- Download Spotify playlists and favorite songs from YouTube.
- Easy login with your Spotify account.
- Metadata and Song Images added to files

## Installation
To get started, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/stzanetis/spotidown.git
cd spotidown
pip install -r requirements.txt
python ./spotidown.py
```

## Important
- Right now you can only use this by creating your own app in spotify web developer and putting your client id and secret to a .env file.
- Binaries for ffmpeg also need to be in the repository directory in order to convert the webm files downloaded from ytdlp to mp3 files.
