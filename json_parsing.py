import random


def collect_recent_tracks(json_data):
    all_recent_song_names = [item.get('track', {}).get('name') for item in json_data.get('items', [])]
    # all_recent_song_names = list(set(all_recent_song_names))

    all_recent_song_previews = [item.get('track', {}).get('preview_url') for item in json_data.get('items', [])]
    # all_recent_song_previews = list(set(all_recent_song_previews))

    res = {}
    for key in all_recent_song_names:
        for value in all_recent_song_previews:
            res[key] = value
            all_recent_song_previews.remove(value)
            break


    random_songs = random.sample(range(0, len(all_recent_song_names) - 1), 10)

    song_names = []
    song_previews = []

    for i in random_songs:
        song_names.append(all_recent_song_names[i])
        song_previews.append(all_recent_song_previews[i])

    return {
        "names": song_names,
        "previews": song_previews,
    }

def get_user_id(json_data):
    return json_data.get('id')
