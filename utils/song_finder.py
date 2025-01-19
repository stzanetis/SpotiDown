# Find the best matching song from the search results
def find_best_song(track, search_results):
    best_score = 0
    best_match = None

    w_name, w_artist, w_duration = 0.5, 0.3, 0.2
    spotify_name = track["track"]["name"].lower()
    spotify_artist = track["track"]["artists"][0]["name"].lower()
    spotify_duration = track["track"]["duration_ms"] / 1000
    for result in search_results:
        youtube_name = result["title"].lower()
        youtube_artist = result["artists"][0]["name"].lower()
        youtube_duration = result["duration_seconds"]

        name_match = sum(1 for char in spotify_name if char in youtube_name) / len(spotify_name)
        artist_match = sum(1 for artist in spotify_artist if artist in youtube_artist) / len(spotify_artist)
        duration_match = 1 - min(1, abs(spotify_duration - youtube_duration) / spotify_duration * 0.1)

        # Penalize unwanted content in the YouTube title unless explicitly stated in Spotify metadata
        penalty_keywords = ['live', 'performance', 'cover', 'karaoke', 'remix', 'rework', 'edit']
        penalty = 0
        for keyword in penalty_keywords:
            if keyword.lower() in youtube_name and keyword.lower() not in spotify_name:
                penalty += 0.1

        score = (w_artist * artist_match + w_name * name_match + w_duration * duration_match - penalty)
        if score > best_score:
            best_score = score
            best_match = result
    return best_match