import requests
import json

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

# Movie and TV show retrieval with filtering
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

# Refresh functions
def refresh_movie(movie_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RefreshMovie",
        "params": {"movieid": movie_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")

def refresh_tvshow(tvshow_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.RefreshTVShow",
        "params": {"tvshowid": tvshow_id},
        "id": 1
    }
    return send_kodi_request(payload).get("result", "Failed")

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
        print("3. Refresh all movies")
        print("4. Refresh all TV shows and episodes")
        print("5. Exit to main menu")
        choice = input("Choose an option (1-5): ")

        if choice == "1":
            search = input("Enter movie search term: ")
            movies = get_movies(search)
            if not movies:
                print("No movies found.")
                continue
            for idx, movie in enumerate(movies):
                print(f"{idx + 1}. {movie['title']} (ID: {movie['movieid']})")
            print(f"{len(movies) + 1}. Exit to previous menu")
            choice = int(input("Enter the number of the movie to refresh or exit: ")) - 1
            if choice == len(movies):
                continue
            movie_id = movies[choice]["movieid"]
            result = refresh_movie(movie_id)
            print(f"Movie refresh result: {result}")
        
        elif choice == "2":
            search = input("Enter TV show search term: ")
            tvshows = get_tvshows(search)
            if not tvshows:
                print("No TV shows found.")
                continue
            for idx, tvshow in enumerate(tvshows):
                print(f"{idx + 1}. {tvshow['title']} (ID: {tvshow['tvshowid']})")
            print(f"{len(tvshows) + 1}. Exit to previous menu")
            choice = int(input("Enter the number of the TV show to refresh or exit: ")) - 1
            if choice == len(tvshows):
                continue
            tvshow_id = tvshows[choice]["tvshowid"]
            result = refresh_tvshow(tvshow_id)
            print(f"TV Show refresh result: {result}")
        
        elif choice == "3":
            print("Refreshing all movies...")
            refresh_all_movies()

        elif choice == "4":
            print("Refreshing all TV shows and their episodes...")
            refresh_all_tvshows()

        elif choice == "5":
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
            print(f"{len(movies) + 1}. Exit to previous menu")
            choice = int(input("Enter the number of the movie to delete or exit: ")) - 1
            if choice == len(movies):
                continue
            movie_id = movies[choice]["movieid"]
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
            print(f"{len(tvshows) + 1}. Exit to previous menu")
            choice = int(input("Enter the number of the TV show to delete or exit: ")) - 1
            if choice == len(tvshows):
                continue
            tvshow_id = tvshows[choice]["tvshowid"]
            result = delete_tvshow(tvshow_id)
            print(f"TV Show delete result: {result}")
        
        elif choice == "3":
            print("Returning to main menu...")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
