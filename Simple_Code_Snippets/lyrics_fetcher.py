import tkinter as tk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
import time
import threading

class LyricsFetcherGUI:
    def __init__(self, master):
        self.master = master
        master.title("Lyrics Fetcher")
        master.geometry("400x300")
        master.wm_attributes("-topmost", 1)  # Always on top

        self.spotify_client_id = "" # Replace with your Spotify Client ID
        self.spotify_client_secret = "" # Replace with your Spotify Client Secret
        self.spotify_redirect_uri = "http://localhost:8888/callback" # Replace with your Spotify Redirect URI
        self.genius_access_token = ""  # Replace with your Genius Access Token

        self.spotify = None
        self.genius = None
        self.current_song = None
        self.lyrics = ""

        self.status_label = tk.Label(master, text="Initializing...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.lyrics_text = tk.Text(master, wrap=tk.WORD)
        self.lyrics_text.pack(expand=True, fill=tk.BOTH)
        self.lyrics_text.config(state=tk.DISABLED) # Make the text widget read-only


        self.authenticate()


    def authenticate(self):
        try:
            self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.spotify_client_id,
                                                           client_secret=self.spotify_client_secret,
                                                           redirect_uri=self.spotify_redirect_uri,
                                                           scope="user-read-currently-playing"))
            self.genius = lyricsgenius.Genius(self.genius_access_token)
            self.status_label.config(text="Ready")
            self.update_lyrics()
        except Exception as e:
            self.status_label.config(text=f"Authentication Failed: {e}")
            print(f"Authentication Error: {e}")

    def get_current_song(self):
        try:
            if self.spotify:
                current_track = self.spotify.current_user_playing_track()
                if current_track and current_track['item']:
                    song_name = current_track['item']['name']
                    artist_name = current_track['item']['artists'][0]['name']
                    return f"{song_name} - {artist_name}"
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error getting current song: {e}")
            self.status_label.config(text=f"Error getting song: {e}")
            return None

    def fetch_lyrics(self, song_title, artist_name):
        try:
            if self.genius:
                song = self.genius.search_song(song_title, artist=artist_name)
                if song:
                    return song.lyrics
                else:
                    return "Lyrics not found."
            else:
                return "Genius API not initialized."
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return f"Error fetching lyrics: {e}"

    def update_lyrics(self):
        threading.Timer(5.0, self.update_lyrics).start()  # Poll every 5 seconds

        song = self.get_current_song()

        if song and song != self.current_song:
            self.current_song = song
            song_name, artist_name = song.split(" - ")
            self.status_label.config(text=f"Now Playing: {song}")
            lyrics = self.fetch_lyrics(song_name, artist_name)
            self.lyrics = lyrics
            self.update_display()
        elif not song:
            self.status_label.config(text="No song playing.")
            if self.current_song:
                self.current_song = None
                self.lyrics = ""
                self.update_display()



    def update_display(self):
        self.lyrics_text.config(state=tk.NORMAL) # Allow editing
        self.lyrics_text.delete("1.0", tk.END)  # Clear existing text
        self.lyrics_text.insert(tk.END, self.lyrics)
        self.lyrics_text.config(state=tk.DISABLED)  # Disable editing


root = tk.Tk()
gui = LyricsFetcherGUI(root)
root.mainloop()