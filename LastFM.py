# lastfm_data.py - MelodyMetrics
import requests

LASTFM_API_KEY = "442a992e54445ae2b1d8e07b9241d707"

def get_lastfm_stats(track_name, artist_name):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getInfo",
        "track": track_name,
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }

    r = requests.get(url, params=params)
    if not r.ok:
        return {"track_name": track_name, "artist_name": artist_name,
                "listeners": 0, "playcount": 0, "tags": []}

    data = r.json().get("track", {})
    listeners = int(data.get("listeners", 0))
    playcount = int(data.get("playcount", 0))

    tags_raw = data.get("toptags", {}).get("tag", [])
    if isinstance(tags_raw, dict):
        tags_raw = [tags_raw]
    tags = [t.get("name") for t in tags_raw if isinstance(t, dict)]

    return {
        "track_name": track_name,
        "artist_name": artist_name,
        "listeners": listeners,
        "playcount": playcount,
        "tags": tags
    }

def get_spotify_audio_features(track_ids, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/audio-features"
    features = {}

    for i in range(0, len(track_ids), 100):
        batch_ids = track_ids[i:i+100]
        params = {"ids": ",".join(batch_ids)}

        r = requests.get(url, headers=headers, params=params)
        if not r.ok:
            continue

        for item in repsonse["audio_features"]:
            if item:
                features[item["id"]] = {
                    "danceability": item.get("danceability"),
                    "energy": item.get("energy"),
                    "tempo": item.get("tempo"),
                    "valence": item.get("valence")
                }

    return features


def store_lastfm_data(cursor, stats):
    cursor.execute(
        "SELECT track_id FROM tracks JOIN artists USING(artist_id) WHERE tracks.name=? AND artists.name=?",
        (stats["track_name"], stats["artist_name"])
    )
    row = cursor.fetchone()
    if not row:
        return

    cursor.execute(
        "INSERT OR REPLACE INTO lastfm_stats VALUES (?, ?, ?, ?)",
        (row[0], stats["listeners"], stats["playcount"], ", ".join(stats["tags"]))
    )
