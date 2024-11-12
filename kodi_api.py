import requests
import json
import time

# Kodi connection details
KODI_IP = "xxx.xxx.xxx.xxx" # Replace with your Kodi IP address
KODI_PORT = 8080
KODI_USERNAME = "xxxx"  # Replace with your Kodi username
KODI_PASSWORD = "xxxx"  # Replace with your Kodi password
KODI_URL = f"http://{KODI_IP}:{KODI_PORT}/jsonrpc"
HEADERS = {'Content-Type': 'application/json'}

def send_kodi_request(payload):
    """Send a JSON-RPC request to Kodi."""
    response = requests.post(KODI_URL, headers=HEADERS, data=json.dumps(payload), auth=(KODI_USERNAME, KODI_PASSWORD))
    response.raise_for_status()
    return response.json()


# Library update and cleaning
def update_library():
    """Update the Kodi library."""
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.Scan",
        "id": 1
    }
    response = send_kodi_request(payload)
    return response.get("result", "Failed to update library")


def clean_library():
    """Clean the Kodi library."""
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.Clean",
        "id": 1
    }
    response = send_kodi_request(payload)
    return response.get("result", "Failed to clean library")


# Movie, TV show, and music video retrieval with filtering
def get_movies(search=""):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {"properties": ["title"]},
        "id": 1
    }
    movies = send_kodi_request(payload).get("result", {}).get("movies", [])
    return [movie for movie in movies if search.lower() in movie['title'].lower()]


def get_tvshows(search=""):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetTVShows",
        "params": {"properties": ["title"]},
        "id": 1
    }
    tvshows = send_kodi_request(payload).get("result", {}).get("tvshows", [])
    return [tvshow for tvshow in tvshows if search.lower() in tvshow['title'].lower()]


def get_music_videos(search=""):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMusicVideos",
        "params": {"properties": ["title"]},
        "id": 1
    }
    music_videos = send_kodi_request(payload).get("result", {}).get("musicvideos", [])
    return [mv for mv in music_videos if search.lower() in mv['title'].lower()]


# Refresh functions
def refresh_movie(movie_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RefreshMovie",
        "params": {"movieid": movie_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")


def refresh_all_movies():
    """Refresh all movies in the Kodi library."""
    # Get the list of all movies
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {"properties": ["title"]},
        "id": 1
    }

    try:
        # Send request to Kodi
        response = send_kodi_request(payload)
        movies = response.get("result", {}).get("movies", [])
        
        if not movies:
            print("No movies found in the library. Response received:", response)
            return

        # Loop through each movie and refresh it
        for movie in movies:
            movie_id = movie.get("movieid")
            movie_title = movie.get("title", "Untitled Movie")
            
            # Refresh the movie metadata
            result = refresh_movie(movie_id)
            print(f"Refreshing movie '{movie_title}' (ID: {movie_id}): {result}")
            time.sleep(0.25)

    except Exception as e:
        print("An error occurred while trying to refresh all movies:", str(e))


def refresh_tvshow(tvshow_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RefreshTVShow",
        "params": {"tvshowid": tvshow_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")


def refresh_tvshow_with_episodes(tvshow_id, tvshow_label=""):
    """Refresh a single TV show and all its episodes."""
    # Refresh the TV show metadata
    result = refresh_tvshow(tvshow_id)
    print(f"Refreshing TV show '{tvshow_label}' (ID: {tvshow_id}): {result}")
    
    # Retrieve all episodes for the specified TV show
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetEpisodes",
        "params": {"tvshowid": tvshow_id},
        "id": 1
    }
    episodes_response = send_kodi_request(payload)
    episodes = episodes_response.get("result", {}).get("episodes", [])
    
    if not episodes:
        print(f"No episodes found for TV show '{tvshow_label}' (ID: {tvshow_id}). Response received:", episodes_response)
        return

    # Refresh each episode individually
    for episode in episodes:
        episode_id = episode.get("episodeid")
        episode_label = episode.get("label", "Untitled Episode")
        
        # Refresh episode metadata
        payload = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.RefreshEpisode",
            "params": {"episodeid": episode_id},
            "id": 1
        }
        episode_result = send_kodi_request(payload).get("result", "Failed")
        print(f" - Refreshing episode '{episode_label}' (ID: {episode_id}): {episode_result}")
        time.sleep(0.25)


def refresh_all_tvshows():
    """Refresh all TV shows and each episode within them."""
    # Get the list of all TV shows without specifying properties
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetTVShows",
        "params": {},
        "id": 1
    }

    try:
        # Send request to Kodi
        response = send_kodi_request(payload)
        tvshows = response.get("result", {}).get("tvshows", [])
        
        if not tvshows:
            print("No TV shows found in the library. Response received:", response)
            return

        # Loop through each TV show and refresh it along with all its episodes
        for tvshow in tvshows:
            tvshow_id = tvshow.get("tvshowid")
            tvshow_title = tvshow.get("label", "Untitled TV Show")  # Use 'label' instead of 'title'
            
            # Refresh the TV show metadata
            result = refresh_tvshow(tvshow_id)
            print(f"Refreshing TV show '{tvshow_title}' (ID: {tvshow_id}): {result}")
            
            # Get episodes for the current TV show
            payload = {
                "jsonrpc": "2.0",
                "method": "VideoLibrary.GetEpisodes",
                "params": {"tvshowid": tvshow_id},
                "id": 1
            }
            episodes_response = send_kodi_request(payload)
            episodes = episodes_response.get("result", {}).get("episodes", [])
            
            if not episodes:
                print(f"No episodes found for TV show '{tvshow_title}' (ID: {tvshow_id}). Response received:", episodes_response)
                continue

            # Refresh each episode in the current TV show
            for episode in episodes:
                episode_id = episode.get("episodeid")
                episode_title = episode.get("label", "Untitled Episode")  # Use 'label' instead of 'title'
                
                payload = {
                    "jsonrpc": "2.0",
                    "method": "VideoLibrary.RefreshEpisode",
                    "params": {"episodeid": episode_id},
                    "id": 1
                }
                episode_result = send_kodi_request(payload).get("result", "Failed")
                print(f" - Refreshing episode '{episode_title}' (ID: {episode_id}): {episode_result}")
                time.sleep(0.25)

    except Exception as e:
        print("An error occurred while trying to refresh all TV shows:", str(e))


def refresh_music_video(music_video_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RefreshMusicVideo",
        "params": {"musicvideoid": music_video_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")


def refresh_all_music_videos():
    """Refresh all music videos in the Kodi library."""
    # Get the list of all music videos
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMusicVideos",
        "params": {"properties": ["title"]},
        "id": 1
    }

    try:
        # Send request to Kodi
        response = send_kodi_request(payload)
        music_videos = response.get("result", {}).get("musicvideos", [])
        
        if not music_videos:
            print("No music videos found in the library. Response received:", response)
            return

        # Loop through each music video and refresh it
        for mv in music_videos:
            music_video_id = mv.get("musicvideoid")
            music_video_title = mv.get("title", "Untitled Music Video")
            
            # Refresh the music video metadata
            result = refresh_music_video(music_video_id)
            print(f"Refreshing music video '{music_video_title}' (ID: {music_video_id}): {result}")
            time.sleep(0.25)

    except Exception as e:
        print("An error occurred while trying to refresh all music videos:", str(e))


# Delete functions
def delete_movie(movie_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RemoveMovie",
        "params": {"movieid": movie_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")

def delete_tvshow(tvshow_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RemoveTVShow",
        "params": {"tvshowid": tvshow_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")


# Main menu options
def main_menu():
    while True:
        print("\nKodi Library Management:")
        print("1. Update Kodi library")
        print("2. Clean Kodi library")
        print("3. Refresh Kodi library")
        print("4. Delete items from Kodi library")
        print("5. Exit")
        choice = input("Choose an option (1-5): ")

        if choice == "1":
            result = update_library()
            print("Library update:", result)
        
        elif choice == "2":
            result = clean_library()
            print("Library clean:", result)
        
        elif choice == "3":
            refresh_menu()
        
        elif choice == "4":
            delete_menu()
        
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

def refresh_menu():
    while True:
        print("\nRefresh Options:")
        print("1. Refresh a specific movie by search")
        print("2. Refresh a specific TV show and episodes by search")
        print("3. Refresh a specific music video by search")
        print("4. Refresh all movies")
        print("5. Refresh all TV shows and episodes")
        print("6. Refresh all music videos")
        print("7. Exit to main menu")
        choice = input("Choose an option (1-7): ")

        if choice == "1":
            search = input("Enter movie search term: ")
            movies = get_movies(search)
            if not movies:
                print("No movies found.")
                continue
            for idx, movie in enumerate(movies):
                print(f"{idx + 1}. {movie['title']} (ID: {movie['movieid']})")
            print(f"{len(movies) + 1}. Exit")
            choice = int(input("Enter the number of the movie to refresh: "))
            if choice == len(movies) + 1:
                continue
            movie_id = movies[choice - 1]["movieid"]
            result = refresh_movie(movie_id)
            print(f"Movie refresh result: {result}")
        
        elif choice == "2":
            search = input("Enter TV show search term: ")
            tvshows = get_tvshows(search)
            if not tvshows:
                print("No TV shows found.")
                continue
            for idx, tvshow in enumerate(tvshows):
                print(f"{idx + 1}. {tvshow['label']} (ID: {tvshow['tvshowid']})")
            choice = int(input("Enter the number of the TV show to refresh (or 0 to exit): ")) - 1
            if choice >= 0:
                tvshow_id = tvshows[choice]["tvshowid"]
                tvshow_label = tvshows[choice].get("label", "Untitled TV Show")
                refresh_tvshow_with_episodes(tvshow_id, tvshow_label)
        
        elif choice == "3":
            search = input("Enter music video search term: ")
            music_videos = get_music_videos(search)
            if not music_videos:
                print("No music videos found.")
                continue
            for idx, mv in enumerate(music_videos):
                print(f"{idx + 1}. {mv['title']} (ID: {mv['musicvideoid']})")
            print(f"{len(music_videos) + 1}. Exit")
            choice = int(input("Enter the number of the music video to refresh: "))
            if choice == len(music_videos) + 1:
                continue
            music_video_id = music_videos[choice - 1]["musicvideoid"]
            result = refresh_music_video(music_video_id)
            print(f"Music video refresh result: {result}")

        elif choice == "4":
            print("Refreshing all movies...")
            refresh_all_movies()

        elif choice == "5":
            print("Refreshing all TV shows and their episodes...")
            refresh_all_tvshows()

        elif choice == "6":
            print("Refreshing all music videos...")
            refresh_all_music_videos()

        elif choice == "7":
            print("Returning to main menu...")
            break

        else:
            print("Invalid option. Please try again.")

def delete_menu():
    while True:
        print("\nDelete Options:")
        print("1. Delete a specific movie by search")
        print("2. Delete a specific TV show and its episodes by search")
        print("3. Exit to main menu")
        choice = input("Choose an option (1-3): ")

        if choice == "1":
            search = input("Enter movie search term: ")
            movies = get_movies(search)
            if not movies:
                print("No movies found.")
                continue
            for idx, movie in enumerate(movies):
                print(f"{idx + 1}. {movie['title']} (ID: {movie['movieid']})")
            print(f"{len(movies) + 1}. Exit")
            choice = int(input("Enter the number of the movie to delete: "))
            if choice == len(movies) + 1:
                continue
            movie_id = movies[choice - 1]["movieid"]
            result = delete_movie(movie_id)
            print(f"Movie delete result: {result}")
        
        elif choice == "2":
            search = input("Enter TV show search term: ")
            tvshows = get_tvshows(search)
            if not tvshows:
                print("No TV shows found.")
                continue
            for idx, tvshow in enumerate(tvshows):
                print(f"{idx + 1}. {tvshow['title']} (ID: {tvshow['tvshowid']})")
            print(f"{len(tvshows) + 1}. Exit")
            choice = int(input("Enter the number of the TV show to delete: "))
            if choice == len(tvshows) + 1:
                continue
            tvshow_id = tvshows[choice - 1]["tvshowid"]
            result = delete_tvshow(tvshow_id)
            print(f"TV Show delete result: {result}")
        
        elif choice == "3":
            print("Returning to main menu...")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
