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

def play_song(song_path):
    pygame.mixer.init()

    try:
        print(f"Playing song: {song_path}")
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

    except pygame.error as e:
        print(f"Error playing song: {e}")


@app.route('/artists', methods=['GET', 'POST'])

def play_artist():
    global currently_playing, is_paused
    songs = ["LilUziVert_XO_tour_life.mp3",
             "LilUziVert_20_Min.mp3",
             "LilUziVert_That_Way.mp3"]

    
    if request.method == 'POST':
        selected_song = request.form.get('selected_song')
        song_path = f"static/songs/{selected_song}" 

        if currently_playing and currently_playing.lower() == song_path.lower():
            
            if is_paused:
                pygame.mixer.music.unpause()
                is_paused = False
                return f"Resumed playing: {selected_song}"
            
            else:
                pygame.mixer.music.pause()
                is_paused = True
                return f"Paused: {selected_song}"
        
        else:
            # Ako je selektirana druga pjesma, zaustavi ovu trenutnu
            if currently_playing:
                pygame.mixer.music.stop()
            play_song(song_path)
            currently_playing = song_path
            is_paused = False
            #return f"Playing: {selected_song}" 
            current_song_name = selected_song
            return render_template('artists.html', songs=songs, current_song_name=current_song_name)
        
    return render_template('artists.html', songs=songs, current_song_name=current_song_name)

@app.route('/albums')

def test(): 
    return render_template('albums.html')

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
    app.run(debug=True)