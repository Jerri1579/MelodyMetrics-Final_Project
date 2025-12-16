#  audiodb.py - interact with the audiodb API
import requests

BASE_URL = "https://www.theaudiodb.com/api/v1/json/2"

def get_artist_info(artist_name):
    url = f"{BASE_URL}/search.php"
    params = {"s": artist_name}

    r = requests.get(url, params=params)
    if not r.ok:
        print("AudioDB error:", r.text)
        return None

    data = r.json()
    if not data or not data.get("artists"):
        return None

    artist = data["artists"][0]

    return {
        "artist_name": artist.get("strArtist"),
        "genre": artist.get("strGenre"),
        "style": artist.get("strStyle"),
        "country": artist.get("strCountry"),
        "mood": artist.get("strMood"),
        "biography": artist.get("strBiographyEN")
    }


def store_audiodb_data(cursor, artist_id, audiodb_data):
    if not audiodb_data:
        return

    cursor.execute("""
        INSERT OR REPLACE INTO audiodb_artists
        (artist_id, genre, style, country, mood, biography)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        artist_id,
        audiodb_data.get("genre"),
        audiodb_data.get("style"),
        audiodb_data.get("country"),
        audiodb_data.get("mood"),
        audiodb_data.get("biography")
    ))
    if not audiodb_data:
        return

    cursor.execute("SELECT id FROM artists WHERE spotify_id = ?", (artist_id,))
    row = cursor.fetchone()
    if not row:
        return  
    artist_db_id = row[0]

    
    cursor.execute("""
        INSERT OR REPLACE INTO audiodb_artists
        (artist_id, genre, style, country, mood, biography)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        artist_db_id,
        audiodb_data.get("genre"),
        audiodb_data.get("style"),
        audiodb_data.get("country"),
        audiodb_data.get("mood"),
        audiodb_data.get("biography")
    ))

    cursor.connection.commit()