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
        if not year: continue
        d = (year // 10) * 10
        decades.setdefault(d, []).append(play)

    return {d: sum(v)/len(v) for d, v in decades.items()}

def calculate_listeners_by_decade(cursor):
    cursor.execute("""
        SELECT release_year, listeners
        FROM tracks JOIN lastfm_stats USING(track_id)
    """)
    rows = cursor.fetchall()

    dvals = {}
    for year, lis in rows:
        if not year: continue
        d = (year // 10) * 10
        dvals.setdefault(d, []).append(lis)

    return dvals

def calculate_genre_trends(cursor):
    cursor.execute("""
        SELECT release_year, top_tags
        FROM tracks JOIN lastfm_stats USING(track_id)
    """)
    rows = cursor.fetchall()

    trends = {}
    for year, tags in rows:
        if not year or not tags: continue
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
    decades = sorted(data)
    values = [data[d] for d in decades]
    plt.figure()
    plt.bar(decades, values)
    plt.title("Popularity by Decade")
    plt.xlabel("Decade")
    plt.ylabel("Avg Playcount")
    plt.tight_layout()
    plt.show()

def plot_scatter_releaseyear_vs_listeners(data):
    years, listeners = [], []
    for decade, vals in data.items():
        for v in vals:
            years.append(decade)
            listeners.append(v)
    plt.figure()
    plt.scatter(years, listeners)
    plt.title("Listeners vs Release Decade")
    plt.xlabel("Decade")
    plt.ylabel("Listeners")
    plt.tight_layout()
    plt.show()

def plot_genre_trends(data):
    plt.figure()
    for genre, vals in data.items():
        decades = sorted(vals)
        counts = [vals[d] for d in decades]
        plt.plot(decades, counts, marker="o", label=genre)
    plt.xlabel("Decade")
    plt.ylabel("Frequency")
    plt.title("Genre Trends Over Time")
    plt.legend()
    plt.tight_layout()
    plt.show()
