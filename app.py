from flask import Flask, render_template, request, url_for
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/weather', methods = ['GET', 'POST'])

def get_weather():
    if request.method == 'POST':
        city_name = request.form['name']

        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=f67dd4f0cf1bb7b76de384a0c4eabd50'
        response = requests.get(url.format(city_name)).json()

        temp = response['main']['temp']
        weather = response['weather'][0]['description']
        min_temp = response['main']['temp_min']
        max_temp = response['main']['temp_max']
        icon = response['weather'][0]['icon']
 
        # empty string ili samo razmaci
        if not bool(city_name.strip()):
            city_name = "Samobor"

        # handlea error 404 -> grad nije pronađen ; cod == 200 -> success
        if not response['cod'] == 200:
            return render_template('city_not_found.html')   

        print(temp,weather,min_temp,max_temp,icon)

        return render_template('weather.html',temp=temp,weather=weather,min_temp=min_temp,max_temp=max_temp,icon=icon, city_name = city_name)
    else:
        return render_template('weather.html')


if __name__ == '__main__':
   app.run(debug=True)
