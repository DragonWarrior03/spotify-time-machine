import spotipy
from spotipy.oauth2 import SpotifyOAuth,SpotifyClientCredentials
from Bill_Board import obtain_bill_board
import pprint
import json
import os

class spotify:
    # # ==================== Get Song Names =======================
    def __init__(self,date,year):
        self.date=date
        self.billboard=obtain_bill_board(date=self.date)
        self.songs=self.billboard.all_songs[0:100]
        self.artists=self.billboard.all_artists[0:100]
        self.year=year



    def create_playlist(self):
        client_id = "91b0b7d20c864eda884a5856f97c0c59"
        os.environ["SPOTIPY_CLIENT_ID"]=client_id
        client_secret = "dde671591e9341c5a953a274f7389b14"
        os.environ["SPOTIPY_CLIENT_SECRET"]=client_secret
        redirect_uri = "http://example.com"
        os.environ["SPOTIPY_REDIRECT_URI"]=redirect_uri


        # # ==================== Spotify API =======================
        spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            cache_path="token.txt",
            scope="playlist-modify-public",
            show_dialog=True
        )
        )

        spotify1=spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            cache_path="token1.txt",
            scope="playlist-read-private",
            show_dialog=True
        ))

        self.sp=spotify.current_user()
        self.user_id = self.sp["id"]
        song_uris=[]
        for n in range(0,len(self.songs)):
            result = spotify.search(q=f"{self.songs[n]} {self.artists[n]} {self.year}", type="track",limit="1")
            try:
                uri = result["tracks"]["items"][0]["uri"]
                song_uris.append(uri)
            except IndexError:
                print(f"{self.songs[n]} by {self.artists[n]} does not exist in spotify. Skipped")

        # # ==================== Create Playlist =======================
        self.playlist=spotify.user_playlist_create(user=self.user_id,name=f"{self.date} Billboard 100" , description=f"Enjoy these top 100 songs from the year {self.year}",public=False)
        playlist_id=self.playlist["id"]

        for uri in song_uris:
            spotify.playlist_add_items(playlist_id=playlist_id,items=[uri])

        self.user_playlist=spotify1.current_user_playlists(limit="50",offset="0")



