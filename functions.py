import os
import time
from flask import redirect, url_for, session
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


#API KEYS HERE
#CLIENT_ID =
#CLIENT_SECRET =
#SECRET_KEY =

def configure():
   load_dotenv()

def create_spotify_oauth():
  return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-top-read user-library-read"
  )

def get_token(TOKEN_INFO):
  token_info = session.get(TOKEN_INFO, None)
  if not token_info:
    return redirect(url_for("login", _external=False))
  now = int(time.time())
  is_expired = token_info['expires_at'] - now < 60
  if is_expired:
      sp_oauth = create_spotify_oauth()
      token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
  return token_info
