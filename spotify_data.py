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
    # detect schema shape for backward/forward compatibility
    cursor.execute("PRAGMA table_info(artists)")
    artist_cols = [r[1] for r in cursor.fetchall()]
    cursor.execute("PRAGMA table_info(tracks)")
    track_cols = [r[1] for r in cursor.fetchall()]

    use_new_artist_cols = 'spotify_artist_id' in artist_cols
    use_new_track_cols = 'spotify_track_id' in track_cols

    for t in tracks:
        if use_new_artist_cols:
            # new schema: artists has integer PK and spotify_artist_id
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO artists (spotify_artist_id, name) VALUES (?, ?)",
                    (t["artist_id"], t["artist"])
                )
            except Exception:
                # fallback to older insert if schema differs
                cursor.execute("INSERT OR IGNORE INTO artists VALUES (?, ?)", (t["artist_id"], t["artist"]))

            cursor.execute("SELECT artist_id FROM artists WHERE spotify_artist_id = ?", (t["artist_id"],))
            row = cursor.fetchone()
            artist_db_id = row[0] if row else None
        else:
            # old schema: artist_id is the Spotify id string primary key
            cursor.execute("INSERT OR IGNORE INTO artists VALUES (?, ?)", (t["artist_id"], t["artist"]))
            artist_db_id = t["artist_id"]

        if use_new_track_cols:
            # new tracks table stores spotify_track_id and integer artist_id
            cursor.execute("SELECT track_id FROM tracks WHERE spotify_track_id = ?", (t["id"],))
            track_row = cursor.fetchone()
            if track_row:
                cursor.execute(
                    "UPDATE tracks SET name = ?, artist_id = ?, release_year = ? WHERE track_id = ?",
                    (t["name"], artist_db_id, t["release_year"], track_row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO tracks (spotify_track_id, name, artist_id, release_year) VALUES (?, ?, ?, ?)",
                    (t["id"], t["name"], artist_db_id, t["release_year"]) 
                )
        else:
            # old tracks schema uses string track_id as primary key
            cursor.execute("""
                INSERT OR REPLACE INTO tracks (track_id, name, artist_id, release_year)
                VALUES (?, ?, ?, ?)
            """, (t["id"], t["name"], artist_db_id, t["release_year"]))
