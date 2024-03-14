import spotipy
import os
import requests
from functions import configure, create_spotify_oauth, get_token
from flask import Flask, request, url_for, session, redirect, render_template

app = Flask(__name__)
app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"
app.secret_key = os.getenv("SECRET_KEY")
TOKEN_INFO = "token_info"

configure()

@app.route("/")
def home():
    return render_template('index.html', title='Unwrapped')

@app.route("/login")
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route("/logout")
def logout():
    session[TOKEN_INFO] = "relogin"
    return redirect("/")

@app.route('/redirectPage')
def redirectPage():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("view", _external=True))

@app.route("/view")
def view():
  time_range = request.args.get('time_range', "short_term")
  try:
      user_token = get_token(TOKEN_INFO)['access_token']
  except Exception as e:
      print(e)
      return redirect("/")

  sp = spotipy.Spotify(auth=user_token)
  user_top_songs = sp.current_user_top_tracks(limit=10, offset=0, time_range=time_range)
  user_top_artists = sp.current_user_top_artists(limit=10, offset=0, time_range=time_range)
  user_info = sp.current_user()
  display_name = user_info['display_name']

  #API Call to recieve image of top artist
  headers = {"Authorization": f"Bearer {session[TOKEN_INFO]['access_token']}"}
  params = {"limit": 10, "offset": 0,"time_range": time_range}
  top_artists_response = requests.get("https://api.spotify.com/v1/me/top/artists", headers=headers, params=params)
  top_artists_data = top_artists_response.json()

  # Extracting the image of the most listened to group
  most_listened_artist_image = top_artists_data['items'][0]['images'][0]['url']

  # Counting the genres
  genre_count = {}
  for artist in top_artists_data['items']:
      for genre in artist['genres']:
          if genre not in genre_count:
              genre_count[genre] = 1
          else:
              genre_count[genre] += 1

  # Determining the top genre
  top_genre = max(genre_count, key=genre_count.get)

  #Cache Deletion
  if os.path.exists(".cache"):
    os.remove(".cache")

  #Renderer
  return render_template('wrapped.html',
                         name=display_name,
                         songs=user_top_songs["items"],
                         artists=user_top_artists["items"],
                         genre=top_genre,
                         image=most_listened_artist_image,
                         range=time_range,
                         title="Your Unwrapped")