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
    songs = [
    'static/music/TheWeeknd_PartyMonster.mp3',
    'static/music/TheWeeknd_TheHills.mp3'
    ];
    # Handlea prazan string ili razmake
    if city is not None and not bool(city.strip()):
        city = "Samobor"

    weather_data = get_current_weather(city)
    
    # Handlea error 404 (city not found); 200 -> success
    if not weather_data['cod'] == 200:
        return render_template('city_not_found.html')

    return render_template (
        "weather.html",
        songs=songs,
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