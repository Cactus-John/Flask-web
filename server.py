from flask import Flask, render_template, request, url_for, redirect
from weather import get_current_weather
from waitress import serve
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

#--------------------------- DATABASE CREATION AND MANAGEMENT ----------------------------#

app.config['SECRET_KEY'] = 'cactusjohn-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1523@localhost:5432/postgres'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    with app.app_context():
        db.create_all()

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=35)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=35)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Login')



@app.route("/signup", methods=['GET', 'POST'])

def signup():
    form = RegistrationForm()

    if form.validate_on_submit():   
         
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        
        db.session.add(new_user)
        db.create_all()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html', title='Sign Up', form=form)



@app.route("/login", methods=['GET', 'POST'])

def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('success'))
            
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/success', methods=['GET', 'POST'])
@login_required
def success():
    return render_template('success.html')
  

#-----------------------------------------------------------------------------------------#
    
    
    
#---------------------------------------- WEATHER REQUESTS -------------------------------#
        
@app.route('/')
def home():
    return render_template('index.html')

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