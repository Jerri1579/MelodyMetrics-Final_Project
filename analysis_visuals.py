# analysis_visuals.py - MelodyMetrics
import csv
import matplotlib.pyplot as plt

def calculate_popularity_by_decade(cursor):
    cursor.execute("""
        SELECT release_year, playcount
        FROM tracks JOIN lastfm_stats USING(track_id)
    """)
    rows = cursor.fetchall()

    decades = {}
    for year, play in rows:
        if not year:
            continue
        d = (year // 10) * 10
        decades.setdefault(d, []).append(play)

    return {d: sum(v)/len(v) for d, v in decades.items()}

def calculate_listeners_by_decade(cursor):
    """
    Return two lists: (years, listeners) for each track.
    Keeping the old name so main.py doesn't have to change.
    """
    cursor.execute("""
        SELECT release_year, listeners
        FROM tracks JOIN lastfm_stats USING(track_id)
        WHERE release_year IS NOT NULL
    """)
    rows = cursor.fetchall()

    years = []
    listeners = []

    for year, lis in rows:
        if year is None:
            continue
        years.append(year)
        listeners.append(lis)

    return years, listeners


def calculate_genre_trends(cursor):
    cursor.execute("""
        SELECT release_year, top_tags
        FROM tracks JOIN lastfm_stats USING(track_id)
    """)
    rows = cursor.fetchall()

    trends = {}
    for year, tags in rows:
        if not year or not tags:
            continue
        d = (year // 10) * 10
        for tag in tags.split(","):
            tag = tag.strip()
            trends.setdefault(tag, {}).setdefault(d, 0)
            trends[tag][d] += 1
    return trends

def write_popularity_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["decade", "avg_popularity"])
        for d in sorted(data):
            w.writerow([d, data[d]])

def plot_popularity_by_decade(data):
    """Bar chart of average playcount by decade (in millions)."""
    if not data:
        print("No data to plot for popularity by decade.")
        return

    decades = sorted(data.keys())
    # convert to millions so axis numbers are smaller
    values_millions = [data[d] / 1_000_000 for d in decades]

    plt.figure()
    plt.barh(decades, values_millions)
    plt.title("Average Track Popularity by Decade")
    plt.xlabel("Average Playcount (millions)")
    plt.ylabel("Decade")
    plt.tight_layout()
    plt.show()

def plot_scatter_releaseyear_vs_listeners(data):
    """
    Scatter plot of release year vs listeners.
    `data` is a tuple: (years, listeners)
    """
    years, listeners = data
    if not years:
        print("No data to plot for listeners vs release year.")
        return

    plt.figure()
    plt.scatter(years, listeners, alpha=0.7)
    plt.title("Listeners vs Release Year")
    plt.xlabel("Release Year")
    plt.ylabel("Listeners")
    plt.tight_layout()
    plt.show()


def plot_genre_trends(data, top_n=7):
    """
    Plot trends over time for the top N most frequent tags.
    `data` = {tag: {decade: count}}
    """
    if not data:
        print("No data to plot for genre trends.")
        return

    # Find top N tags by total count
    totals = {tag: sum(decades.values()) for tag, decades in data.items()}
    top_tags = sorted(totals, key=totals.get, reverse=True)[:top_n]

    plt.figure()
    for tag in top_tags:
        decade_data = data[tag]
        decades = sorted(decade_data.keys())
        counts = [decade_data[d] for d in decades]
        plt.plot(decades, counts, marker="o", label=tag)

    plt.xlabel("Decade")
    plt.ylabel("Tag Frequency")
    plt.title(f"Top {top_n} Tag Trends Over Time")
    # put legend outside plot so it doesn't cover the lines
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)
    plt.tight_layout()
    plt.show()

def plot_artist_listeners_by_decade(cursor, artists):
    """
    Grouped bar chart: average listeners by artist & decade.
    Decades: 2000s, 2010s, 2020s.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    # Define the decade buckets
    decades = {
        "2000s": (2000, 2009),
        "2010s": (2010, 2019),
        "2020s": (2020, 2024),
    }

    # Initialize structure: {artist: {decade_label: [listeners,...]}}
    data = {artist: {dec: [] for dec in decades} for artist in artists}

    # Pull all relevant rows once
    cursor.execute("""
        SELECT a.name, t.release_year, ls.listeners
        FROM tracks t
        JOIN artists a ON t.artist_id = a.artist_id
        JOIN lastfm_stats ls ON t.track_id = ls.track_id
        WHERE t.release_year BETWEEN 2000 AND 2024
    """)
    rows = cursor.fetchall()

    # Bucket rows into artist + decade
    for name, year, listeners in rows:
        if name not in artists or year is None:
            continue
        for label, (start, end) in decades.items():
            if start <= year <= end:
                data[name][label].append(listeners)
                break

    # Convert lists to averages
    avg_results = {artist: {} for artist in artists}
    for artist in artists:
        print(f"\n{artist}:")  # DEBUG
        for label in decades.keys():
            vals = data[artist][label]
            if vals:
                avg_val = sum(vals) / len(vals)
            else:
                avg_val = 0
            avg_results[artist][label] = avg_val
            print(f"  {label} -> {len(vals)} tracks, avg listeners = {avg_val:.0f}")

    # --- Plotting ---
    decade_labels = list(decades.keys())
    x = np.arange(len(decade_labels))  # 0,1,2
    width = 0.15

    plt.figure(figsize=(12, 6))

    for idx, artist in enumerate(artists):
        artist_vals = [avg_results[artist][dec] for dec in decade_labels]
        plt.bar(x + idx * width, artist_vals, width, label=artist)

    plt.xticks(x + width * (len(artists) - 1) / 2, decade_labels)
    plt.ylabel("Average Listeners")
    plt.title("Average Listeners by Artist and Decade")
    plt.legend()
    plt.tight_layout()
    plt.show()



