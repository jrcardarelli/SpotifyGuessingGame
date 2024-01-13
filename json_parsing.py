import random


def collect_recent_tracks(json_data):
    all_recent_song_names = [item.get('track', {}).get('name') for item in json_data.get('items', [])]
    all_recent_song_previews = [item.get('track', {}).get('preview_url') for item in json_data.get('items', [])]
    all_recent_song_artists = [item.get('track', {}).get('artist') for item in json_data.get('items', [])]
    all_recent_song_covers = [item.get('track', {}).get('album', {}).get('images', [{}])[0].get('url') for item in json_data.get('items', [])]
    all_recent_song_date = [item.get('track', {}).get('release_date') for item in json_data.get('items', [])]

    res = {}
    for key in all_recent_song_names:
        for value in all_recent_song_previews:
            res[key] = value
            all_recent_song_previews.remove(value)
            break

    res2 = {}
    for key in all_recent_song_names:
        for value in all_recent_song_artists:
            res2[key] = value
            all_recent_song_artists.remove(value)
            break

    res3 = {}
    for key in all_recent_song_names:
        for value in all_recent_song_covers:
            res3[key] = value
            all_recent_song_covers.remove(value)
            break

    res4 = {}
    for key in all_recent_song_names:
        for value in all_recent_song_date:
            res4[key] = value
            all_recent_song_date.remove(value)
            break

    all_recent_song_names = list(set(all_recent_song_names))

    random_songs = random.sample(all_recent_song_names, 10)

    result_previews = []
    for song in random_songs:
        result_previews.append(res.get(song))

    result_artists = []
    for song in random_songs:
        result_artists.append(res2.get(song))

    result_covers = []
    for song in random_songs:
        result_covers.append(res3.get(song))

    result_date = []
    for song in random_songs:
        result_date.append(res4.get(song))

    return {
        "names": random_songs,
        "previews": result_previews,
        "durations": result_artists,
        "covers": result_covers,
        "dates": result_date,
    }


def get_user_id(json_data):
    return json_data.get('id')
