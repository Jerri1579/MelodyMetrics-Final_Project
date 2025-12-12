# main.py - Melody Metrics (PURE GENRE VERSION)
from billboard_api import fetch_billboard_hot100
from database import insert_billboard_data
from database import connect_db, create_tables
from spotify_data import get_spotify_tracks, store_spotify_data
from LastFM import get_lastfm_stats, store_lastfm_data
from analysis_visuals import (
    calculate_popularity_by_decade,
    calculate_listeners_by_decade,
    calculate_genre_trends,
    write_popularity_csv,
    plot_popularity_by_decade,
    plot_listener_histogram,
    plot_genre_trends,
    get_top_genres,
    calculate_avg_listeners_by_genre_and_decade,
    plot_listener_histogram,
    plot_listeners_by_genre_and_decade,
    plot_billboard_ranks,
    plot_rank_distribution,
    get_combined_music_data,
    plot_combined_music_data

)

# ----------------------------------------------
# 1. GENRE SEARCH LIST (15 GENRES)
# ----------------------------------------------
GENRE_QUERIES = [
    "genre:pop",
    "genre:rnb",
    "genre:rock",
    "genre:hip hop",
    "genre:rap",
    "genre:electropop",
    "genre:alternative",
    "genre:indie",
    "genre:country",
    "genre:latin",
    "genre:gospel",
    "genre:soul",
    "genre:reggaeton",
    "genre:metal",
    "genre:edm",
]

def run_spotify_pipeline(cursor):
   
    all_tracks = []

    for q in GENRE_QUERIES:
        print("Fetching", q)
        tracks = get_spotify_tracks(q)  # limit=25 already applied
        store_spotify_data(cursor, tracks)
        all_tracks.extend(tracks)

    return all_tracks


def run_lastfm_pipeline(cursor, tracks):
   
    count = 0

    for t in tracks:
        if count >= 25 * len(GENRE_QUERIES):   # reasonable safety limit
            break
        
        stats = get_lastfm_stats(t["name"], t["artist"])
        store_lastfm_data(cursor, stats)
        count += 1


def run_analysis(cursor):
    # --- Popularity by decade ---
    pop = calculate_popularity_by_decade(cursor)
    write_popularity_csv(pop, "popularity_by_decade.csv")
    plot_popularity_by_decade(pop)

    # --- Listener histogram ---
    years, listeners = calculate_listeners_by_decade(cursor)
    plot_listener_histogram((years, listeners))

    # --- Genre trend (top 7 tags) ---
    trends = calculate_genre_trends(cursor)
    plot_genre_trends(trends, top_n=7)

    # --- GENRE ANALYSIS: TOP 15 GENRES ---
    top15 = get_top_genres(cursor, top_n=15)
    print("Top 15 genres (LastFM tags):", top15)

    genre_decade_data = calculate_avg_listeners_by_genre_and_decade(cursor, top15)
    plot_listeners_by_genre_and_decade(genre_decade_data)




def main():
    conn, cursor = connect_db("music_project.db")
    create_tables(cursor)
    conn.commit()

    tracks = run_spotify_pipeline(cursor)
    conn.commit()

    run_lastfm_pipeline(cursor, tracks)
    conn.commit()

    print("Fetching Billboard Hot 100 data...")
    hot_100 = fetch_billboard_hot100(limit=50)
    insert_billboard_data(cursor, hot_100)
    conn.commit()
    print("Billboard data insertion complete.")

    # --- Billboard visuals ---
    try:
        plot_billboard_ranks(hot_100)
    except Exception as e:
        print("Failed to plot Billboard ranks:", e)

    try:
        plot_rank_distribution(cursor)
    except Exception as e:
        print("Failed to plot Billboard rank distribution:", e)


    try:
        rows = get_combined_music_data(cursor, limit=100)
        plot_combined_music_data(rows)
    except Exception as e:
        print("Failed combined Billboard/Spotify/LastFM plot:", e)

    run_analysis(cursor)
    conn.close()




if __name__ == "__main__":
    main()
