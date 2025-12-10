import billboard

def get_top_song(chart_name="hot-100"):
    """
    Fetches the top song from the specified Billboard chart.
    Args:
        chart_name (str): The name of the Billboard chart to fetch.
                          Default is "hot-100".
    Returns:
        dict: A dictionary containing details of the top song.
    """
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