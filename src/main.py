import sys
import os
from spotipy import Spotify
from auth_service import authenticate_spotify, authenticate_youtube, logout_spotify
from playlist_service import get_playlists, migrate_playlist
from auth_service import stop_callback_server, check_server_running
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

VERSION = "1.0.0"
AUTHOR = "Sanniv Choudhuri"

def clear_terminal():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    sp = None
    yt = None
    clear_terminal()

    print(Fore.CYAN + Style.BRIGHT + "🎵 Welcome to Spotify to YouTube Migrator 🎥")
    print(Fore.CYAN + "========================================")
    print(Fore.CYAN + f"Version: {VERSION} | Author: {AUTHOR}")
    print(Fore.CYAN + "========================================")
    print(Fore.GREEN + "1. Show Spotify Playlists " + Fore.YELLOW + "📜")
    print(Fore.GREEN + "2. Migrate Playlist to YouTube " + Fore.RED + "➡️")
    print(Fore.GREEN + "3. Logout from Spotify " + Fore.MAGENTA + "🔒")
    print(Fore.GREEN + "4. Exit " + Fore.RED + "❌")

    while True:
        print(Fore.CYAN + "========================================")
        choice = input(Fore.YELLOW + "Enter your choice: ")

        if choice == "1":
            if sp is None:
                sp = Spotify(auth=authenticate_spotify())
            print(Fore.BLUE + "Fetching Spotify playlists... 📜")
            get_playlists(sp)

        elif choice == "2":
            if sp is None:
                sp = Spotify(auth=authenticate_spotify())
            
            print(Fore.BLUE + "Authenticating with YouTube... 🔐")
            if yt is None:
                yt = youtube = authenticate_youtube()

            print(Fore.BLUE + "Starting playlist migration... 🚀")
            migrate_playlist(sp, youtube)

        elif choice == "3":
            print(Fore.MAGENTA + "Logging out from Spotify... 🔒")
            logout_spotify()
            sp = None

        elif choice == "4":
            print(Fore.RED + "Exiting application. Goodbye! 👋")
            sys.exit(0)
            break

        else:
            print(Fore.RED + "Invalid choice. Please try again. ❌")

if __name__ == "__main__":
    main()
