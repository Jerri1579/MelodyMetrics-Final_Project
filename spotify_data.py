# spotify_data.py - MelodyMetrics (No Audio Features)
import requests, base64

SPOTIFY_CLIENT_ID = "4189c4815c644331a007d54c25e4e923"
SPOTIFY_CLIENT_SECRET = "9ae97fa64e3b41c0a9500c2e02eba51c"

_SPOTIFY_ACCESS_TOKEN = None

def get_spotify_access_token():
    global _SPOTIFY_ACCESS_TOKEN
    if _SPOTIFY_ACCESS_TOKEN:
        return _SPOTIFY_ACCESS_TOKEN

    url = "https://accounts.spotify.com/api/token"
    creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    creds_b64 = base64.b64encode(creds.encode()).decode()
    headers = {"Authorization": f"Basic {creds_b64}"}
    data = {"grant_type": "client_credentials"}

    r = requests.post(url, headers=headers, data=data)
    if not r.ok:
        print("Token error:", r.text)
        r.raise_for_status()

    _SPOTIFY_ACCESS_TOKEN = r.json()["access_token"]
    return _SPOTIFY_ACCESS_TOKEN

def get_auth_headers():
    return {"Authorization": f"Bearer {get_spotify_access_token()}"}

def get_audio_features(track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    r = requests.get(url, headers=get_auth_headers())
    if not r.ok:
        return None
    return r.json()

def get_spotify_tracks(query):
    url = "https://api.spotify.com/v1/search"
    params = {"q": query, "type": "track", "limit": 25}

    r = requests.get(url, headers=get_auth_headers(), params=params)
    if not r.ok:
        print("Search error:", r.text)
        return []   # 🔑 NEVER return None

    items = r.json().get("tracks", {}).get("items", [])
    results = []

    for item in items:
        album = item.get("album", {})
        release = album.get("release_date", "1900")
        year = int(release[:4]) if release[:4].isdigit() else 1900

        track_id = item.get("id")
        if not track_id:
            continue

        
        results.append({
            "id": track_id,
            "name": item.get("name"),
            "artist": item.get("artists", [{}])[0].get("name"),
            "artist_id": item.get("artists", [{}])[0].get("id"),
            "release_year": year
        })

    return results

def store_spotify_data(cursor, tracks):
        for t in tracks:
          
            cursor.execute(
                "INSERT OR IGNORE INTO artists (spotify_id, name) VALUES (?, ?)",
                (t["artist_id"], t["artist"])
            )
            cursor.execute("SELECT id FROM artists WHERE spotify_id = ?", (t["artist_id"],))
            artist_db_id = cursor.fetchone()[0]

          
            cursor.execute("SELECT id FROM tracks WHERE spotify_id = ?", (t["id"],))
            track_row = cursor.fetchone()
            if track_row:
                cursor.execute(
                    "UPDATE tracks SET name = ?, artist_id = ?, release_year = ? WHERE id = ?",
                    (t["name"], artist_db_id, t["release_year"], track_row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO tracks (spotify_id, name, artist_id, release_year) VALUES (?, ?, ?, ?)",
                    (t["id"], t["name"], artist_db_id, t["release_year"]) 
                )
