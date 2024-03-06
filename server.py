from flask import Flask, render_template, request, jsonify
from weather import get_current_weather
from waitress import serve


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


@app.route('/artists', methods=['GET', 'POST'])

def play_artist():
    # Fetch songs data from database or other source
    songs = [
        {'title': '20 Min', 'filename': 'LilUziVert_20_Min.mp3'},
        {'title': 'Aye', 'filename': 'LilUziVert_Aye.mp3'},
    ]
    
    return render_template('artists.html', songs=songs)


"""
is_playing = False
is_paused = False
currently_playing = None
current_song_name = None
selected_filename = None
current_sound = None

def play_song(song_path):
    global current_sound
    current_sound = pygame.mixer.Sound(song_path)
    current_sound.play()


@app.route('/artists', methods=['GET', 'POST'])

def play_artist():

    global currently_playing, is_paused, is_playing, current_song_name, selected_filename, current_sound
    
    selected_song = None
    song_path = None
    
    songs = [
        {'title': 'XO Tour Life', 'filename': 'LilUziVert_XO_tour_life.mp3', 'image': url_for('static', filename='images/album1.jpg')},
        {'title': '20 Min', 'filename': 'LilUziVert_20_Min.mp3', 'image': url_for('static', filename='images/album1.jpg')},
        {'title': 'Aye', 'filename': 'LilUziVert_Aye.mp3', 'image': url_for('static', filename='images/album2.png')},
        {'title': 'Flooded The Face', 'filename': 'LilUziVert_Flooded_The_Face.mp3', 'image': url_for('static', filename='images/album2.png')},
        {'title': 'Pluto to Mars', 'filename': 'LilUziVert_Pluto_to_Mars.mp3', 'image': url_for('static', filename='images/album2.png')},
        {'title': 'That Way', 'filename': 'LilUziVert_That_Way.mp3', 'image': url_for('static', filename='images/album1.jpg')},
        {'title': 'Erase Your Social', 'filename': 'LilUziVert_Erase_Your_Social.mp3', 'image': url_for('static', filename='images/album3.jpg')},
    ]
    
    pygame.init()
    pygame.mixer.init()
    
    if request.method == 'POST':
        selected_song = request.form.get('selected_song')
        
        # Find the selected song in the list
        matching_songs = [song for song in songs if song['title'] == selected_song]
        
        if matching_songs:
            selected_filename = matching_songs[0]['filename']
            song_path = os.path.join("static/songs", selected_filename)
            
            if os.path.isfile(song_path):
                play_song(song_path)
                currently_playing = selected_song
            else:
                print(f"File does not exist: {song_path}")
        
            current_song_name = selected_song
    
        if request.form.get('play') == 'Play':
            if not is_playing:
                if current_sound:
                    current_sound.unpause()
                else:
                    play_song(os.path.join("static/songs", selected_filename))
                is_playing = True
                is_paused = False
            
        if request.form.get('restart') == 'true':
            if current_sound:
                current_sound.stop()
                play_song(os.path.join("static/songs", selected_filename))
                is_paused = False

        if request.form.get('pause') == 'Pause':
             if current_sound and selected_filename:
                current_sound.pause()
                is_paused = True

        if request.form.get('resume') == 'Resume':
            if current_sound and is_paused:
                current_sound.unpause()
                is_paused = False
                is_playing = True 

    return render_template('artists.html', 
                           songs=songs, 
                           current_song_name=current_song_name, 
                           is_paused=is_paused, 
                           is_playing=is_playing) 
                           
"""


@app.route('/albums')

def test(): 
    return render_template('albums.html')

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
    #app.run(host="0.0.0.0", port=5000, debug=True)