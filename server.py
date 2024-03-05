from flask import Flask, render_template, request
from weather import get_current_weather
from waitress import serve
import pygame

app = Flask(__name__)

@app.route('/')

def home():
    return render_template('index.html')

@app.route('/weather', methods = ['GET', 'POST'])

def get_weather():
    city = request.args.get('city')
    
    # Handlea prazan string ili razmake
    if city is not None and not bool(city.strip()):

        city = "Samobor"

    weather_data = get_current_weather(city)
    
    # Handlea error 404 (city not found); 200 -> success
    if not weather_data['cod'] == 200:

        return render_template('city_not_found.html')

    return render_template (
        "weather.html",
        title=weather_data["name"],
        status=weather_data["weather"][0]["description"].capitalize(),
        temp=f"{weather_data['main']['temp']:.1f}",
        icon=weather_data["weather"][0]["icon"],
        feels_like=f"{weather_data['main']['feels_like']:.1f}"
    )

currently_playing = None
is_paused = False
is_playing = False

def play_song(song_path):
    pygame.mixer.init()

    try:

        print(f"Playing song: {song_path}")
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

    except pygame.error as e:

        print(f"Error playing song: {e}")


@app.route('/artists', methods=['POST'])

def play_artist():

    global currently_playing, is_paused, is_playing
    
    selected_song = None
    song_path = None
    
    album_image_path = ["../static/images/album1.jpg",
                        "../static/images/album2.png",
                        "../static/images/album3.jpg"]

    songs = ["LilUziVert_XO_tour_life.mp3",
             "LilUziVert_20_Min.mp3",
             "LilUziVert_That_Way.mp3",
             "LilUziVert_Flooded_The_Face.mp3",
             "LilUziVert_Erase_Your_Social.mp3"]
    
    album_art = {
        songs[0]: album_image_path[0],
        songs[1]: album_image_path[0],
        songs[2]: album_image_path[0],
        songs[3]: album_image_path[1],
        songs[4]: album_image_path[2]
    }

    def get_album_image(song_name):
        return album_art.get(song_name, 'default-image.jpg') 
    
    pygame.init()
    pygame.mixer.init()
    
    if request.method == 'POST':

        selected_song = request.form.get('selected_song')
        song_path = f"static/songs/{selected_song.strip()}"

        current_song_name = selected_song
        album_image_path = get_album_image(current_song_name)

        pygame.init()
        pygame.mixer.init()

        if request.form.get('play') == 'Play':

            # provjera ako muzika jos nije playana
            
            if not is_playing:  
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                is_playing = True
                is_paused = False
            
        elif request.form.get('pause') == 'Pause':

            # pauza ako muzika playa i nije pauza
            
            if is_playing and not is_paused:  
                pygame.mixer.music.pause()
                is_paused = True
                

        if request.form.get('restart') == 'true':
            
            #restartaj pjsemu ispocetka na restart 
            
            if currently_playing:

                pygame.mixer.music.rewind()
                pygame.mixer.music.play()
                is_paused = False
               

        if currently_playing and currently_playing == song_path:
            
            #play i pause
            
            if is_paused:

                pygame.mixer.music.unpause()
                is_paused = False
               
            else:

                pygame.mixer.music.pause()
                is_paused = True
                
        else:
        
            if currently_playing:
                pygame.mixer.music.stop()

            play_song(song_path)
            currently_playing = song_path
            is_paused = False
            
        
    #if song_path:
    #   sound = pygame.mixer.Sound(song_path)
    #   total_duration = sound.get_length()
    #else:
    #   total_duration = 0.0

    #song_position = pygame.mixer.music.get_pos() / 1000.0  # milliseconds to seconds
        
    return render_template('artists.html', 
                           songs=songs, 
                           current_song_name=None,
                           album_image_path=album_image_path)


@app.route('/albums')

def test(): 
    return render_template('albums.html')

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
    app.run(debug=True)