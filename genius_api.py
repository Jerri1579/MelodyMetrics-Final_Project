API_KEY= "I5Pn3qd2jqOOAveuvQYJaMwRBLGES8tKTD68FijZ9FwAUiO2XIMfV8AnVvzX8Bsh"

# genius_api.py - MelodyMetrics
import requests
GENIUS_TOKEN = API_KEY
GENIUS_API_URL = "https://api.genius.com"

headers = {
    "Authorization": f"Bearer{GENIUS_TOKEN}"
}

def search_song(track_name, artist_name):
    query = f"{track_name} {artist_name}"
    url = f"{GENIUS_API_URL}/search"
    params = {"q": query}
    r = requests.get(url, headers=headers, params=params)
    if not r.ok:
        print("Genius search error:", r.text)
        r.raise_for_status()

    hits = r.json().get("response", {}).get("hits", [])
    for hit in hits:
        result = hit.get("result", {})
        if (result.get("title", "").lower() == track_name.lower() and
                result.get("primary_artist", {}).get("name", "").lower() == artist_name.lower()):
            return result

    return None

def get_song_info(track_name, artist_name):
    result = search_song(track_name, artist_name)
    if not result:
        return None

    song_info = {
        "id": result.get("id"),
        "title": result.get("title"),
        "artist": result.get("primary_artist", {}).get("name"),
        "url": result.get("url")
    }
    return song_info


