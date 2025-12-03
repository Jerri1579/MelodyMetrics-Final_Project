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

def get_spotify_tracks(query):
    url = "https://api.spotify.com/v1/search"
    params = {"q": query, "type": "track", "limit": 25}
    r = requests.get(url, headers=get_auth_headers(), params=params)
    if not r.ok:
        print("Search error:", r.text)
        r.raise_for_status()

    items = r.json().get("tracks", {}).get("items", [])
    results = []

    for item in items:
        album = item.get("album", {})
        release = album.get("release_date", "1900")
        year = int(release[:4]) if release[:4].isdigit() else 1900

        results.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "artist": item.get("artists", [{}])[0].get("name"),
            "artist_id": item.get("artists", [{}])[0].get("id"),
            "release_year": year,
        })
    return results

def store_spotify_data(cursor, tracks):
    for t in tracks:
        cursor.execute(
            "INSERT OR IGNORE INTO artists VALUES (?, ?)",
            (t["artist_id"], t["artist"])
        )

        cursor.execute("""
            INSERT OR REPLACE INTO tracks (track_id, name, artist_id, release_year)
            VALUES (?, ?, ?, ?)
        """, (t["id"], t["name"], t["artist_id"], t["release_year"]))
