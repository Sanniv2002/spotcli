from spotipy import Spotify
import colorama
from colorama import Fore, Style
from googleapiclient.errors import HttpError

colorama.init()

# Get all Spotify playlists
def get_playlists(sp: Spotify):
    playlists = sp.current_user_playlists()
    print(Fore.CYAN + "Your Spotify Playlists:" + Style.RESET_ALL)
    if not playlists["items"]:
        print(Fore.RED + "⚠️ No playlists found." + Style.RESET_ALL)
        return

    for idx, playlist in enumerate(playlists["items"], 1):
        print(f"{idx}. {playlist['name']} ({playlist['tracks']['total']} tracks)")

# Fetch existing videos in a YouTube playlist
def get_existing_video_ids(youtube, playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids.extend(
            item["snippet"]["resourceId"]["videoId"]
            for item in response.get("items", [])
        )

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids

# Add videos to a YouTube playlist in batchess
from googleapiclient.errors import HttpError
from colorama import Fore, Style

def add_videos_to_playlist(youtube, playlist_id, video_ids):
    success_count = 0
    failure_count = 0

    print(Fore.CYAN + f"⏳ Adding {len(video_ids)} videos to playlist: {playlist_id}" + Style.RESET_ALL)

    for idx, video_id in enumerate(video_ids):
        print(Fore.CYAN + f"⏳ Adding video {idx + 1}/{len(video_ids)} (Video ID: {video_id})..." + Style.RESET_ALL)

        try:
            response = youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }
                }
            ).execute()

            if response and response.get("id"):
                success_count += 1
                print(Fore.GREEN + f"✅ Successfully added video: {video_id}" + Style.RESET_ALL)
            else:
                failure_count += 1
                print(Fore.RED + f"⚠️ Failed to add video: {video_id} (No response ID returned)" + Style.RESET_ALL)

        except HttpError as http_err:
            failure_count += 1
            error_content = http_err.content.decode('utf-8') if hasattr(http_err, 'content') else "No content available"
            print(Fore.RED + f"⚠️ HTTP error for video {video_id}: {http_err}" + Style.RESET_ALL)
            print(Fore.RED + f"⚠️ Error details: {error_content}" + Style.RESET_ALL)

        except Exception as e:
            failure_count += 1
            print(Fore.RED + f"⚠️ Unexpected error for video {video_id}: {e}" + Style.RESET_ALL)

    print(Fore.CYAN + f"\nProcessing complete: {success_count} videos added, {failure_count} failed." + Style.RESET_ALL)
    return success_count, failure_count





# Migrate selected Spotify playlist to YouTube
def migrate_playlist(sp, youtube):
    playlists = sp.current_user_playlists()
    if not playlists["items"]:
        print(Fore.RED + "⚠️ No Spotify playlists available for migration." + Style.RESET_ALL)
        return

    print(Fore.CYAN + "Available Playlists:" + Style.RESET_ALL)
    for idx, playlist in enumerate(playlists["items"], 1):
        print(Fore.YELLOW + f"{idx}. {playlist['name']} ({playlist['tracks']['total']} tracks)" + Style.RESET_ALL)

    try:
        choice = int(input(Fore.GREEN + "Select a playlist to migrate by number: " + Style.RESET_ALL)) - 1
        if not (0 <= choice < len(playlists["items"])):  # Check if the input is valid
            raise ValueError
    except ValueError:
        print(Fore.RED + "⚠️ Invalid selection. Please enter a valid number." + Style.RESET_ALL)
        return

    selected_playlist = playlists["items"][choice]
    total_tracks = selected_playlist["tracks"]["total"]
    print(Fore.CYAN + f"\nMigrating playlist: {selected_playlist['name']} ({total_tracks} tracks)..." + Style.RESET_ALL)

    # Fetch all tracks in the selected playlist
    tracks = sp.playlist_tracks(selected_playlist["id"])
    track_names = [(track["track"]["name"], track["track"]["artists"][0]["name"]) for track in tracks["items"]]

    # Create a new YouTube playlist
    youtube_playlist = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": selected_playlist["name"], "description": "Migrated from Spotify"},
            "status": {"privacyStatus": "public"}
        }
    ).execute()

    playlist_id = youtube_playlist["id"]

    # Fetch existing video IDs
    existing_video_ids = get_existing_video_ids(youtube, playlist_id)
    print(Fore.CYAN + f"Found {len(existing_video_ids)} existing videos in the YouTube playlist." + Style.RESET_ALL)

    # Search for videos and add to playlist
    video_ids_to_add = []
    for track_name, artist_name in track_names:
        print(Fore.MAGENTA + f"Searching for {track_name} by {artist_name}..." + Style.RESET_ALL)
        search_response = youtube.search().list(
            q=f"{track_name} {artist_name}",
            part="snippet",
            maxResults=5
        ).execute()

        video_id = None
        for item in search_response.get("items", []):
            video_title = item["snippet"]["title"].lower()
            if track_name.lower() in video_title and artist_name.lower() in video_title:
                video_id = item["id"]["videoId"]
                break

        if video_id and video_id not in existing_video_ids:
            video_ids_to_add.append(video_id)

    # Batch process video additions
    if video_ids_to_add:
        try:
            success_count, failure_count = add_videos_to_playlist(youtube, playlist_id, video_ids_to_add)
            print(Fore.CYAN + "\nPlaylist migration complete!" + Style.RESET_ALL)
            print(Fore.GREEN + f"✅ Successfully migrated {success_count} tracks." + Style.RESET_ALL)
            print(Fore.RED + f"⚠️ Failed to migrate {failure_count} tracks." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"⚠️ Error during batch execution: {e}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "⚠️ No valid videos found to add to the playlist." + Style.RESET_ALL)

