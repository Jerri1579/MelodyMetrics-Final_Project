# analysis_visuals.py - Melody Metrics (genre-focused)

import csv
import matplotlib.pyplot as plt
import numpy as np


def calculate_popularity_by_decade(cursor):
    """
    Returns {decade: avg_playcount} using Spotify + LastFM.
    """
    cursor.execute("""
        SELECT release_year, playcount
        FROM tracks
        JOIN lastfm_stats USING(track_id)
    """)
    rows = cursor.fetchall()

    decades = {}
    for year, play in rows:
        if not year:
            continue
        decade = (year // 10) * 10
        decades.setdefault(decade, []).append(play)

    return {d: sum(vals) / len(vals) for d, vals in decades.items()}


def calculate_listeners_by_decade(cursor):
 
    cursor.execute("""
        SELECT release_year, listeners
        FROM tracks
        JOIN lastfm_stats USING(track_id)
        WHERE release_year IS NOT NULL
    """)
    rows = cursor.fetchall()

    years = []
    listeners = []
    for year, lis in rows:
        years.append(year)
        listeners.append(lis)

    return years, listeners


def calculate_genre_trends(cursor):
    """
    Returns {tag: {decade: count}} showing how often each tag appears per decade.
    Tags are treated as 'genres'.
    """
    cursor.execute("""
        SELECT release_year, top_tags
        FROM tracks
        JOIN lastfm_stats USING(track_id)
    """)
    rows = cursor.fetchall()

    trends = {}
    for year, tags_str in rows:
        if not year or not tags_str:
            continue
        decade = (year // 10) * 10

        for tag in tags_str.split(","):
            t = tag.strip().lower()
            if not t:
                continue
            trends.setdefault(t, {}).setdefault(decade, 0)
            trends[t][decade] += 1

    return trends




def write_popularity_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["decade", "avg_popularity"])
        for d in sorted(data.keys()):
            writer.writerow([d, data[d]])



def plot_popularity_by_decade(data):
    if not data:
        print("No data to plot for popularity by decade.")
        return

    decades = sorted(data.keys())
    values_millions = [data[d] / 1_000_000 for d in decades]

    plt.figure(figsize=(8, 5))
    plt.barh(decades, values_millions)
    plt.title("Average Track Popularity by Decade")
    plt.xlabel("Average Playcount (millions)")
    plt.ylabel("Decade")
    plt.tight_layout()
    plt.show()


def plot_listener_histogram(data):
    """
    Histogram of listener counts instead of scatter.
    `data` is (years, listeners)
    """
    years, listeners = data
    if not listeners:
        print("No data to plot for listener histogram.")
        return

    plt.figure(figsize=(10, 6))
    plt.hist(listeners, bins=20, edgecolor="black", alpha=0.7)
    plt.title("Distribution of Listener Counts")
    plt.xlabel("Listeners")
    plt.ylabel("Number of Tracks")
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()



def plot_genre_trends(trends, top_n=7):
   
    if not trends:
        print("No data to plot for genre trends.")
        return

    # pick top N genres by total count
    totals = {tag: sum(dec_counts.values()) for tag, dec_counts in trends.items()}
    top_tags = sorted(totals, key=totals.get, reverse=True)[:top_n]

    plt.figure(figsize=(10, 6))
    for tag in top_tags:
        dec_map = trends[tag]
        decades = sorted(dec_map.keys())
        counts = [dec_map[d] for d in decades]
        plt.plot(decades, counts, marker="o", label=tag)

    plt.xlabel("Decade")
    plt.ylabel("Tag Frequency")
    plt.title(f"Top {top_n} Tag (Genre) Trends Over Time")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)
    plt.tight_layout()
    plt.show()


def get_top_genres(cursor, top_n=15):
 
    cursor.execute("""
        SELECT top_tags
        FROM lastfm_stats
        WHERE top_tags IS NOT NULL AND top_tags <> ''
    """)
    rows = cursor.fetchall()

    counts = {}
    for (tags_str,) in rows:
        for tag in tags_str.split(","):
            t = tag.strip().lower()
            if not t:
                continue
            counts[t] = counts.get(t, 0) + 1

    # sort tags by frequency
    sorted_tags = sorted(counts, key=counts.get, reverse=True)
    return sorted_tags[:top_n]


def calculate_avg_listeners_by_genre_and_decade(cursor, genres):
    """
    Returns:
        { genre: { "2000s": avg_listeners, "2010s": ..., "2020s": ... } }
    using LastFM listeners + release_year + tags.
    """
    decades = {
        "2000s": (2000, 2009),
        "2010s": (2010, 2019),
        "2020s": (2020, 2024),
    }

    # initialize structure
    data = {g: {label: [] for label in decades} for g in genres}

    cursor.execute("""
        SELECT t.release_year, ls.listeners, ls.top_tags
        FROM tracks t
        JOIN lastfm_stats ls USING(track_id)
        WHERE t.release_year IS NOT NULL
    """)
    rows = cursor.fetchall()

    for year, listeners, tags_str in rows:
        if not tags_str:
            continue

        # figure out which decade bucket this year belongs to
        decade_label = None
        for label, (start, end) in decades.items():
            if start <= year <= end:
                decade_label = label
                break
        if decade_label is None:
            continue

        tags = [tag.strip().lower() for tag in tags_str.split(",") if tag.strip()]
        for g in genres:
            if g in tags:
                data[g][decade_label].append(listeners)

    # convert lists to averages
    avg_data = {}
    for g in genres:
        avg_data[g] = {}
        for label in decades.keys():
            vals = data[g][label]
            avg_data[g][label] = sum(vals) / len(vals) if vals else 0

    return avg_data



def plot_listeners_by_genre_and_decade(genre_data):
 
    if not genre_data:
        print("No genre data to plot.")
        return

    genres = sorted(genre_data.keys())
    decades = ["2000s", "2010s", "2020s"]
    x = np.arange(len(genres))
    width = 0.25

    plt.figure(figsize=(14, 6))

    for i, decade in enumerate(decades):
        vals = [genre_data[g].get(decade, 0) for g in genres]
        plt.bar(x + i * width, vals, width, label=decade)

    plt.xticks(x + width, genres, rotation=45, ha="right")
    plt.ylabel("Average Listeners")
    plt.title("Average Listeners by Genre and Decade")
    plt.legend(title="Decade")
    plt.tight_layout()
    plt.show()


def get_combined_music_data(cursor, limit=100):
    cursor.execute(f"""
        SELECT
        t.name,
        t.release_year,
        lf.listeners,
        lf.playcount,
        g.lyrics
        FROM tracks t
        JOIN lastfm_stats lf USING(track_id)
        JOIN genius_songs g USING(track_id)
        WHERE lf.listeners IS NOT NULL
    """)
    
    return cursor.fetchall()