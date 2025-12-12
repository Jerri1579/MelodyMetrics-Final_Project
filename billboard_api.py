import billboard
import requests


def get_top_song(chart_name="hot-100"):
    chart = billboard.ChartData(chart_name)
    if not chart or len(chart) == 0:
        return None

    top_song = chart[0]
    return {
        "title": top_song.title,
        "artist": top_song.artist,
        "rank": top_song.rank,
        "last_week_rank": top_song.lastPos,
        "peak_rank": top_song.peakPos,
        "weeks_on_chart": top_song.weeks,
    }
    return avg_data 

def fetch_billboard_hot100(limit=50):

    billboard.ChartData._headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }

    chart = billboard.ChartData("hot-100")
    top_songs = []
    for i in range(min(limit, len(chart))):
        song = chart[i]
        top_songs.append({
            "title": song.title,
            "artist": song.artist,
            "rank": song.rank,
            "last_week_rank": song.lastPos,
            "peak_rank": song.peakPos,
            "weeks_on_chart": song.weeks,
        })
    return top_songs