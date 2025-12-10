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
        CREATE TABLE IF NOT EXISTS billboard_stats (
            track_id TEXT PRIMARY KEY,
            rank INTEGER,
            last_week_rank INTEGER,
            peak_rank INTEGER,
            weeks_on_chart INTEGER,
            FOREIGN KEY (track_id) REFERENCES tracks(track_id)
        );
    """)


