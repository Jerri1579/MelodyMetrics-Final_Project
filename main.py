
# main.py - MelodyMetrics (No Audio Features)
from database import connect_db, create_tables
from spotify_data import get_spotify_tracks, store_spotify_data
from LastFM import get_lastfm_stats, store_lastfm_data
from analysis_visuals import (
    calculate_popularity_by_decade,
    calculate_listeners_by_decade,
    calculate_genre_trends,
    write_popularity_csv,
    plot_popularity_by_decade,
    plot_scatter_releaseyear_vs_listeners,
    plot_genre_trends,
    plot_artist_listeners_by_decade
    
)

def run_spotify_pipeline(cursor):
    all_tracks = []

    queries = [
        
    # Beyoncé by decade
    "artist:Beyoncé year:2000-2009",
    "artist:Beyoncé year:2010-2019",
    "artist:Beyoncé year:2020-2024",

    # Chris Brown
    "artist:Chris Brown year:2000-2009",
    "artist:Chris Brown year:2010-2019",
    "artist:Chris Brown year:2020-2024",

    # Maroon 5
    "artist:Maroon 5 year:2000-2009",
    "artist:Maroon 5 year:2010-2019",
    "artist:Maroon 5 year:2020-2024",

    # Paramore
    "artist:Paramore year:2000-2009",
    "artist:Paramore year:2010-2019",
    "artist:Paramore year:2020-2024",

    # Rihanna
    "artist:Rihanna year:2000-2009",
    "artist:Rihanna year:2010-2019",
    "artist:Rihanna year:2020-2024",

    ]

    for q in queries:
        print("Fetching from Spotify:", q)
        tracks = get_spotify_tracks(q)
        store_spotify_data(cursor, tracks)
        all_tracks.extend(tracks)

    return all_tracks


def run_lastfm_pipeline(cursor, tracks):
   
    seen_per_artist = {}

    for t in tracks:
        artist = t["artist"]

        # Initialize counter
        seen_per_artist.setdefault(artist, 0)

        # Limit to 25 tracks per artist
        if seen_per_artist[artist] >= 25:
            continue

        stats = get_lastfm_stats(t["name"], artist)
        store_lastfm_data(cursor, stats)

        seen_per_artist[artist] += 1




def run_analysis(cursor):

    # DEBUG: see which artist names we actually have
    cursor.execute("SELECT DISTINCT name FROM artists")
    print("Artists in DB:", [row[0] for row in cursor.fetchall()])
    
    # ... rest of your function ...

    pop = calculate_popularity_by_decade(cursor)
    listeners = calculate_listeners_by_decade(cursor)
    genres = calculate_genre_trends(cursor)

    write_popularity_csv(pop, "popularity_by_decade.csv")
    plot_popularity_by_decade(pop)
    plot_scatter_releaseyear_vs_listeners(listeners)
    plot_genre_trends(genres)

    
    plot_artist_listeners_by_decade(cursor, [
        "Beyoncé",
        "Chris Brown",
        "Maroon 5",
        "Paramore",
        "Rihanna"
    ])


def main():
    conn, cursor = connect_db("music_project.db")
    create_tables(cursor)
    conn.commit()

    tracks = run_spotify_pipeline(cursor)
    conn.commit()

    run_lastfm_pipeline(cursor, tracks)
    conn.commit()

    run_analysis(cursor)
    conn.close()

if __name__ == "__main__":
    main()
