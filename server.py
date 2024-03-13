from flask import Flask, render_template, request, url_for, redirect, session, flash
from weather import get_current_weather
from dotenv import load_dotenv
import sqlite3 as sql
import pygame

load_dotenv()

app = Flask(__name__)

#--------------------------- DATABASE CREATION AND MANAGEMENT ----------------------------#


app.secret_key = "my_secret_key"

conn = sql.connect('db_users.db')
print ("Opened database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
print ("Table created successfully")
conn.close()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            # Check if the username already exists
            with sql.connect("db_users.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                existing_user = cur.fetchone()

                if existing_user:
                    flash('Account with this username already exists. Please choose a different username.', 'error')
                    return render_template("signup.html")

                # If the username doesn't exist, proceed with signup
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                con.commit()

                # Log in the user after successful signup
                cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                user = cur.fetchone()


                if user:
                    # Store user_id in the session to mark them as logged in
                    session['user_id'] = user[0]
                    session['username'] = username
                    flash('Signup and login successful', 'success')
                    return redirect(url_for('dashboard'))

        except Exception as e:
            con.rollback()
            flash(f"Error in signup: {str(e)}", 'error')

        finally:
            con.close()

    return render_template("signup.html")

            
@app.route("/login", methods=["GET", "POST"])            
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            with sql.connect("db_users.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                user = cur.fetchone()

                if user:
                    # Log in the user by storing their ID in the session
                    session['user_id'] = user[0]
                    session['username'] = username
                    flash('Login successful', 'success')
                    return redirect(url_for('dashboard'))
                
                else:
                    flash('Invalid username or password', 'error')

        except Exception as e:
            flash('Error during login', 'error')
            print(str(e))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        username = session['username']
        # Retrieve user information from the database using the session ID
        with sql.connect("db_users.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
            user = cur.fetchone()

        if user:
            return render_template("dashboard.html", user=user, username=username)

    # If user is not logged in, redirect to the login page
    flash('You need to login first', 'error')
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    # Clear the session to log out the user
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


#-----------------------------------------------------------------------------------------#
    



#----------------------------------- MUSIC HANDLER ---------------------------------------#



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


@app.route('/music', methods=['GET', 'POST'])

def play_music():

    global currently_playing, is_paused, is_playing
    
    selected_song = None
    song_path = None
    
    album_image_path = ["../static/images/bbtm.png",
                        "../static/images/starboy.png"]

    songs = ["TheWeeknd_TheHills.mp3",
             "TheWeeknd_PartyMonster.mp3"]
    
    album_art = {
        songs[0]: album_image_path[0],
        songs[1]: album_image_path[1],
    }

    def get_album_image(song_name):
        return album_art.get(song_name, 'default-image.jpg') 
    
    pygame.init()
    
    if request.method == 'POST':

        selected_song = request.form.get('selected_song')
        song_path = f"static/music/{selected_song.strip()}"

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
                return render_template('music.html', 
                                       songs=songs, 
                                       current_song_name=selected_song,
                                       album_image_path=album_image_path)
               
            else:

                pygame.mixer.music.pause()
                is_paused = True
                return render_template('music.html', 
                                       songs=songs, 
                                       current_song_name=selected_song,
                                       album_image_path=album_image_path)
                
        else:
        
            if currently_playing:
                pygame.mixer.music.stop()

            play_song(song_path)
            currently_playing = song_path
            is_paused = False
            return render_template('music.html', 
                                    songs=songs, 
                                    current_song_name=selected_song,
                                    album_image_path=album_image_path)
    
    
    return render_template('music.html', 
                           songs=songs, 
                           current_song_name=None,
                           album_image_path=album_image_path)
    
    
    
 #-----------------------------------------------------------------------------------------#
 


#---------------------------------------- WEATHER REQUESTS -------------------------------#
        
@app.route('/')
def home():
    print(session)
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        return render_template("index.html", user_id=user_id, username=username)
    else:
        return render_template("index.html")

@app.route('/weather', methods=['GET', 'POST'])

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
    
#-----------------------------------------------------------------------------------------#

if __name__ == "__main__":
    
    #serve(app, host="0.0.0.0", port=8000)
    
    app.run(host="0.0.0.0", port=8000, debug=True)