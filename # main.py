# main.py - MelodyMetrics
from database import connect_db, create_tables
from spotify_data import (
    get_spotify_tracks,
    get_spotify_audio_features,
    store_spotify_data
)
from lastfm_data import (
    get_lastfm_stats,
    store_lastfm_data
)
from analysis_visuals import (
    calculate_popularity_by_decade,
    calculate_listeners_by_decade,
    calculate_genre_trends,
    write_popularity_csv,
    plot_popularity_by_decade,
    plot_scatter_releaseyear_vs_listeners,
    plot_genre_trends
)

def run_spotify_pipeline(cursor):
    all_tracks = []
    queries = ["Ariana Grande", "Taylor Swift", "Drake", "Bad Bunny", "Beyonce"]

    for q in queries:
        print("Fetching:", q)
        tracks = get_spotify_tracks(q)
        ids = [t["id"] for t in tracks if t.get("id")]

        try:
            features = get_spotify_audio_features(ids)
        except Exception as e:
            print("Audio features blocked:", e)
            features = []

        store_spotify_data(cursor, tracks, features)
        all_tracks.extend(tracks)

    return all_tracks

def run_lastfm_pipeline(cursor, tracks):
    for t in tracks[:25]:
        stats = get_lastfm_stats(t["name"], t["artist"])
        store_lastfm_data(cursor, stats)

def run_analysis(cursor):
    pop = calculate_popularity_by_decade(cursor)
    listeners = calculate_listeners_by_decade(cursor)
    genres = calculate_genre_trends(cursor)

    write_popularity_csv(pop, "popularity_by_decade.csv")
    plot_popularity_by_decade(pop)
    plot_scatter_releaseyear_vs_listeners(listeners)
    plot_genre_trends(genres)

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
