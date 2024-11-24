import os
import socketserver
import http.server
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
from config import Config
from dotenv import load_dotenv
import threading
from google_auth_oauthlib.flow import InstalledAppFlow
import socket
from ytmusicapi import YTMusic

load_dotenv()


def custom_http_request(http, postproc, uri, method, body, headers, methodId, resumable=None):
    if headers is None:
        headers = {}
    headers['referrerPolicy'] = 'no-referrer'
    
    # Create and return the HttpRequest object with the modified headers
    request = HttpRequest(http, postproc, uri, method, body, headers, methodId, resumable)
    
    return request

def authenticate_spotify():
    """
    Authenticate the user via Spotify OAuth and return an access token.
    """
    try:
        # Stop any pprevious runnig servers
        stop_callback_server()
    except Exception:
        pass

    sp_auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope="user-library-read playlist-read-private",
        open_browser=True
    )

    print("\n🔑 Please authenticate with Spotify using the following URL:")
    print(sp_auth.get_authorize_url())

    # Start the callback server to handle the redirect
    if check_server_running(port=8888):
        pass
    else:
        server = start_callback_server(port=8888)


    try:
        # Wait until the auth_code is received
        while server.auth_code is None:
            pass

        # Get the access token using the authorization code
        token_info = sp_auth.get_access_token(server.auth_code)
        print("🎉 Spotify authenticated successfully!")
        return token_info["access_token"]
    except Exception as e:
        print("\n❌ Authentication failed!")
        print(f"Error: {str(e)}")
        raise
    finally:
        # Stop the callback server after authentication
        # stop_callback_server(server)
        pass

# YouTube Authentication

def authenticate_youtube():
    """
    Authenticate the user via YouTube OAuth 2.0 and return an authorized API client.
    """

    try:
        # Stop any previous runnig servers
        stop_callback_server(port=8080)
    except Exception:
        pass
    # Scopes required for playlist modification
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Start OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", scopes
    )
    credentials = flow.run_local_server(port=8080)  # Redirect URI port

    # Build the YouTube API client with OAuth2 credentials
    youtube = build(
        "youtube", "v3", credentials=credentials,
        requestBuilder=custom_http_request,
    )
    print(youtube)
    print("✅ YouTube authenticated successfully!")
    return youtube

def logout_spotify():
    """
    Log out the user by clearing cached token information.
    """
    cache_path = ".cache"  # Default cache file created by spotipy
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print("✅ Successfully logged out from Spotify.")
    else:
        print("⚠️ No active Spotify session found.")

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for processing callback requests."""
    def do_GET(self):
        if "code" in self.path:
            # Extract the authorization code and save it to the server
            self.server.auth_code = self.path.split("code=")[1].split("&")[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authentication successful! You may now close this window.")
            # Stop the server gracefully
            threading.Thread(target=self.server.shutdown).start()

def start_callback_server(port=8888):
    """Starts the callback server to handle OAuth redirection."""
    server = socketserver.TCPServer(("", port), CallbackHandler)
    server.auth_code = None

    # Run the server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    # print(f"Callback server running on http://localhost:{port}/callback")
    return server

def stop_callback_server(server):
    """Stops the callback server."""
    if server:
        server.shutdown()
        server.server_close()
        print("Callback server has been stopped.")

def check_server_running(port, host="127.0.0.1"):
    """
    Check if a server is running on a specific host and port.
    
    :param host: The host or IP address of the server (e.g., "localhost", "127.0.0.1").
    :param port: The port number to check (e.g., 8080, 80).
    :return: True if the server is running, False otherwise.
    """
    try:
        # Try to establish a connection to the server on the given port
        with socket.create_connection((host, port), timeout=5):
            return True
    except (socket.timeout, socket.error):
        return False