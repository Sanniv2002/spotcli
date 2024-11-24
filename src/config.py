import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    YOUTUBE_API_KEY = os.getenv("YT_MUSIC_API_KEY")
