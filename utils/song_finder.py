import re
from collections import Counter
from difflib import SequenceMatcher

def find_best_song1(track, search_results_song, search_results_video):
    best_song = None
    best_song_score = 0
    best_video = None
    best_video_score = 0

    w_name, w_artist, w_duration = 0.4, 0.2, 0.4
    spotify_name = track["track"]["name"].lower()
    spotify_artist = track["track"]["artists"][0]["name"].lower()
    spotify_duration = track["track"]["duration_ms"] / 1000

    #print(f"Spotify song: {spotify_name}")
    for result in search_results_song:
        youtube_name = result["title"].lower()
        youtube_artist = result["artists"][0]["name"].lower()
        youtube_duration = result.get("duration_seconds")
        if youtube_duration is None:
            continue
        
        #track_info(result, track)

        # Basic matching
        name_match = match_percentage(spotify_name, youtube_name)
        #print("Name match", name_match)
        artist_match = match_percentage(spotify_artist, youtube_artist)
        #print("Artist match", artist_match)
        duration_match = 1 - min(abs(spotify_duration - youtube_duration) / spotify_duration, 1)

        penalty = 0
        if name_match < 0.3 or artist_match < 0.3:
            penalty = 0.5

        score = (w_name * name_match + w_artist * artist_match + w_duration * duration_match) - penalty

        if score > best_song_score:
            best_song_score = score
            best_song = result

    #print("\n")
    best_video_boosts = {"artist_boosted": False, "explicit_boosted": False, "official_boosted": False}
    for result in search_results_video: 
        bvb =  {"artist_boosted": False, "explicit_boosted": False, "official_boosted": False}
        youtube_name = result["title"].lower()
        youtube_artist = result["artists"][0]["name"].lower()
        youtube_duration = result.get("duration_seconds")
        if youtube_duration is None:
            continue

        # Basic matching
        name_match = match_percentage(spotify_name, youtube_name)
        artist_match = match_percentage(spotify_artist, youtube_artist)
        duration_match = 1 - min(abs(spotify_duration - youtube_duration) / spotify_duration, 1)
        
        # Penalize unwanted content
        penalty_keywords = ['live', 'performance', 'cover', 'karaoke', 'remix', 'rework', 'edit', 'clean', 'radio edit', 'censored']
        penalty = 0
        for keyword in penalty_keywords:
            if keyword in youtube_name and keyword not in spotify_name:
                penalty += 0.7
        
        # Calculate base score
        score = (w_name * name_match + w_artist * artist_match + w_duration * duration_match) - penalty
        
        #track_info(result, track)

        # Check for artist in result title
        artist_in_title = match_percentage(spotify_artist, youtube_name)
        if spotify_artist in youtube_name or artist_in_title > 0.6:
            score += 0.5 * artist_in_title
            bvb['artist_boosted'] = True
        
        # Boost if title suggests explicit content
        explicit_keywords = ["explicit", "uncensored", "dirty", "parental advisory"]
        if any(keyword in youtube_name for keyword in explicit_keywords):
            score += 0.2
            bvb['explicit_boosted'] = True
        
        # Boost official videos which tend to be uncensored originals
        if 'official' in youtube_name:
            score += 0.15
            bvb['official_boosted'] = True
        
        #print(f"Final score: {score}")
        if score > best_video_score:
            best_video_score = score
            best_video = result
            best_video_boosts = bvb

    norm = 1
    if best_video_boosts['artist_boosted']:
        norm += 0.2
    if best_video_boosts['explicit_boosted']:
        norm += 0.2
    if best_video_boosts['official_boosted']:
        norm += 0.1

    #print(f"Best song score: {best_song_score:.2f}")
    #print(f"Best video score: {best_video_score:.2f}    Best video song norm: {best_video_score / norm:.2f}")
    #print("Norm", norm)
    if best_song_score > (best_video_score / norm):
        return best_song
    else:
        return best_video

# Find the best matching song from the search results
def find_best_song(track, search_results):
    best_score = 0
    best_match = None
    
    w_name, w_artist, w_duration = 0.4, 0.2, 0.4
    spotify_name = track["track"]["name"].lower()
    spotify_artist = track["track"]["artists"][0]["name"].lower()
    spotify_duration = track["track"]["duration_ms"] / 1000
    
    for result in search_results:
        youtube_name = result["title"].lower()
        youtube_artist = result["artists"][0]["name"].lower()
        youtube_duration = result.get("duration_seconds")
        if youtube_duration is None:
            continue
        
        track_info(result, track)
        
        # Basic matching
        name_match = match_percentage(spotify_name, youtube_name)
        artist_match = match_percentage(spotify_artist, youtube_artist)
        duration_match = 1 - min(abs(spotify_duration - youtube_duration) / spotify_duration, 1)
        
        # Penalize unwanted content
        penalty_keywords = ['live', 'performance', 'cover', 'karaoke', 'remix', 'rework', 'edit', 'clean', 'radio edit', 'censored']
        penalty = 0
        for keyword in penalty_keywords:
            if keyword in youtube_name and keyword not in spotify_name:
                penalty += 0.7
        
        # Calculate base score
        score = (w_name * name_match + w_artist * artist_match + w_duration * duration_match) - penalty
        
        # Check for artist in result title
        artist_in_title = match_percentage(spotify_artist, youtube_name)
        if artist_in_title > 0.6:
            score += 0.5 * artist_in_title
            print(f"Artist '{spotify_artist}' found in title - applied boost: {0.5 * artist_in_title:.2f}")


        # Boost if title suggests explicit content
        explicit_keywords = ["explicit", "uncensored", "dirty", "parental advisory"]
        if any(keyword in youtube_name for keyword in explicit_keywords):
            score += 0.2
        
        # Boost official videos which tend to be uncensored originals
        official_keywords = ['official video', 'official music video', 'official audio', 'official lyric video', 'official music', 'official']
        if any(keyword in youtube_name for keyword in official_keywords):
            score += 0.1
        
        print(f"Final score: {score}")
        # Update best match if better score OR same score but more views
        if score > best_score:
            best_score = score
            best_match = result
    return best_match

def match_percentage(s1, s2, alpha=0.5):
    s1, s2 = s1.lower(), s2.lower()

    # Remove content inside parentheses from s2
    s1, s2 = s1.strip(), s2.strip()
    s2 = re.sub(r'\([^)]*\)', '', s2).strip()
    
    base_score = direct_score(s1, s2, alpha)
    s1_has_greek, s2_has_greek = contains_greek(s1), contains_greek(s2)

    # Greek Title, Latin Match
    if s1_has_greek and not s2_has_greek:
        s1_latin = greek_to_latin(s1)
        trans_score = direct_score(s1_latin, s2, alpha)
        return max(base_score, trans_score)
    
    # Latin Title, Greek Match
    if s2_has_greek and not s1_has_greek:
        s2_latin = greek_to_latin(s2)
        trans_score = direct_score(s1, s2_latin, alpha)
        return max(base_score, trans_score)
    return base_score

def direct_score(s1, s2, alpha=0.5):
    substring_boost = 0.3 if s2 in s1 else 0.0
    freq_sim = char_frequency_similarity(s1, s2)
    pos_sim = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    return min(alpha * pos_sim + (1 - alpha) * freq_sim + substring_boost, 1)

def char_frequency_similarity(s1, s2):
    s1, s2 = s1.lower(), s2.lower()
    c1, c2 = Counter(s1), Counter(s2)
    intersection = sum(min(c1[ch], c2[ch]) for ch in c1.keys() & c2.keys())
    union = sum(c1.values()) + sum(c2.values()) - intersection
    return intersection / union if union else 0

def greek_to_latin(text):
    result = ''
    mapping = { 'α': 'a', 'β': 'v', 'γ': 'g', 'δ': 'd', 'ε': 'e',
                'ζ': 'z', 'η': 'i', 'θ': 'th', 'ι': 'i', 'κ': 'k',
                'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o',
                'π': 'p', 'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't',
                'υ': 'u', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
                'ά': 'a', 'έ': 'e', 'ή': 'i', 'ί': 'i', 'ό': 'o',
                'ύ': 'y', 'ώ': 'o', 'ϊ': 'i', 'ϋ': 'y'}
    for char in text.lower():
        result += mapping.get(char, char)
    return result

def latin_to_greek(text):
    # Process common digraphs first
    text = text.lower()
    text = text.replace('th', 'θ').replace('ch', 'χ').replace('ps', 'ψ')
    result = ''
    mapping = { 'a': 'α', 'v': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε',
                'z': 'ζ', 'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 
                'n': 'ν', 'x': 'ξ', 'o': 'ο', 'p': 'π', 'r': 'ρ', 
                's': 'σ', 't': 'τ', 'y': 'υ', 'f': 'φ', 'w': 'ω',
                'u': 'υ'}
    i = 0
    while i < len(text):
        if text[i] == 's' and (i == len(text)-1 or not text[i+1].isalpha()):
            result += 'ς'
        else:
            result += mapping.get(text[i], text[i])
        i += 1
    return result

def contains_greek(text):
    greek_chars = set('αβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋΐΰΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ')
    return any(char in greek_chars for char in text)

# Debug Function
def track_info(result, track):
    print(f"Spotify song: {track['track']['name']}")
    url = "https://www.youtube.com/watch?v=" + result['videoId']
    print(f" - YouTube song: {result['title']} - URL: {url}")
    print(f" - YouTube artist: {result['artists'][0]['name']}")