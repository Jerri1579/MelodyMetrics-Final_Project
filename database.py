# database.py - MelodyMetrics
import sqlite3

def connect_db(filename):
    conn = sqlite3.connect(filename)
    return conn, conn.cursor()

def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_id TEXT UNIQUE,
            name TEXT
        );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_id TEXT UNIQUE,
            name TEXT,
            artist_id INTEGER,
            release_year INTEGER,
            tempo REAL,
            danceability REAL,
            energy REAL,
            FOREIGN KEY (artist_id) REFERENCES artists(id)
    );
""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lastfm_stats (
            track_id INTEGER PRIMARY KEY,
            listeners INTEGER,
            playcount INTEGER,
            top_tags TEXT,
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audiodb_artists (
        artist_id INTEGER PRIMARY KEY,
        genre TEXT,
        style TEXT,
        country TEXT,
        mood TEXT,
        biography TEXT,
        FOREIGN KEY (artist_id) REFERENCES artists(id)
        );
    """)


