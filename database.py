# database.py - MelodyMetrics
import sqlite3

def connect_db(filename):
    conn = sqlite3.connect(filename)
    return conn, conn.cursor()

def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            artist_id TEXT PRIMARY KEY,
            name TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            track_id TEXT PRIMARY KEY,
            name TEXT,
            artist_id TEXT,
            release_year INTEGER,
            FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lastfm_stats (
            track_id TEXT PRIMARY KEY,
            listeners INTEGER,
            playcount INTEGER,
            top_tags TEXT,
            FOREIGN KEY (track_id) REFERENCES tracks(track_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BillboardHot100 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank INTEGER,
            title TEXT,
            artist TEXT,
            weeks_on_chart INTEGER,
            peak_position INTEGER,
            last_position INTEGER,
            date TEXT
        )
    """)

def insert_billboard_data(cursor, songs):
    """
    Insert Hot 100 chart data into the database.
    
    songs: list of dictionaries, each with:
        - rank
        - title
        - artist
        - weeks_on_chart
        - peak_position
        - last_position
        - date
    """
    for s in songs:
        cursor.execute("""
            INSERT INTO BillboardHot100 (
                rank, title, artist, weeks_on_chart, 
                peak_position, last_position, date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            s.get("rank"),
            s.get("title"),
            s.get("artist"),
            s.get("weeks_on_chart"),
            s.get("peak_position"),
            s.get("last_position"),
            s.get("date")
        ))
