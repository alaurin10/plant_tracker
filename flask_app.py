from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from config import DevelopmentConfig


# Initialize app
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.secret_key = 'stuff'
db = SQLAlchemy(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the email server for sending notifications
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'plant.tracker.notification@gmail.com'
app.config['MAIL_PASSWORD'] = 'uhzfjowrlrxozifa'
mail = Mail(app)

# Create class for user profiles. 
# Each user has a username and email associated with them
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    plants = db.relationship('Plant', backref='user', lazy=True)
  
# Create class for setting up a plant. Initializes plant variables in the database
# Created plants are associated with the user that creates them
class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days_between_watering = db.Column(db.Integer, nullable=False)
    last_watered = db.Column(db.Date, nullable=False)
    next_watering = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Plant {self.name}>'        
 
 # Main page of the app
@app.route('/', methods=['GET', 'POST']) 
@login_required
def index():
    # Method for when user clicks 'Water Now'
    # Updates 'last_watered' and 'next_watering'. Refreshes the page with the new data
    if request.method == 'POST':
        name = request.form['name']
        days_between_watering = request.form['days_between_watering']
        last_watered = datetime.now()
        next_watering = last_watered + timedelta(days=int(days_between_watering))

        plant = Plant(name=name, days_between_watering=days_between_watering, last_watered=last_watered, next_watering=next_watering)
        db.session.add(plant)
        db.session.commit()

        return redirect(url_for('index'))
        
    # Method for when redirected to page
    # Fetches all plants for current user. Also calculates next watering date. Renders page with updated plant info
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    for plant in plants:
        plant.next_watering = plant.last_watered + timedelta(days=plant.days_between_watering)
    return render_template('index.html', plants=plants)

# Page for adding the first plant. Only supports POST method
@app.route('/add_first_plant', methods=['POST'])
@login_required
def add_first_plant():
    # Retrieves data for the first plant and commits it to the current user's database
    # Redirects to add_plant_page
    name = request.form['name']
    last_watered = datetime.strptime(request.form['last_watered'], '%Y-%m-%d')
    days_between_watering = request.form['days_between_watering']
    new_plant = Plant(name=name, last_watered=last_watered, days_between_watering=days_between_watering, user_id=current_user.id)
    db.session.add(new_plant)
    db.session.commit() 
    return redirect(url_for('add_plant_page'))

# Page for adding additional plants. Supports GET and POST methods
@app.route('/add_plant', methods=['GET', 'POST'])
@login_required
def add_plant():
    # Method for when user adds a new plant. Commits new plant to the current user's database
    if request.method == 'POST':
        name = request.form['name']
        last_watered = datetime.strptime(request.form['last_watered'], '%Y-%m-%d')
        days_between_watering = request.form['days_between_watering']
        new_plant = Plant(name=name, last_watered=last_watered, days_between_watering=days_between_watering, user_id=current_user.id)
        db.session.add(new_plant)
        db.session.commit() 
        return redirect(url_for('add_plant_page'))
    
    # Method for when redirected to page
    # Loads and displays all plants for the current user
    else:
        plants = Plant.query.filter_by(user_id=current_user.id).all()
        if not plants:
            return render_template('add_first_plant.html', plants=None)
        return render_template('add_plant.html', plants=plants)

# Page for deleting plants from the current user.
@app.route('/delete_plant/<int:id>', methods=['POST'])
@login_required
def delete_plant(id):
    # Method for when the user deletes a plant. Removes the plant from the current user's database
    if request.method == 'POST':
        plant = Plant.query.filter_by(user_id=current_user.id, id=id).first()
        db.session.delete(plant)
        db.session.commit()
        return redirect(url_for('delete_plant_page'))
    

# Method for watering a plant and updating its date info
@app.route('/water/<int:id>')
@login_required
def water_plant(id):
    # Updates the 'last_watered' variable for the selected plant. Redirects to main page
    plant = Plant.query.filter_by(user_id=current_user.id, id=id).first()
    plant.last_watered = datetime.now().date()
    db.session.commit()
    return redirect('/')
    
# Method for redirecting to delete plant page
# Loads and displays all plants for the current user
# If user deletes all plants, redirects to main page
@app.route('/delete_plant', methods=['GET'])
@login_required
def delete_plant_page():
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    if not plants:
        return redirect(url_for('index'))
    return render_template('delete_plant.html', plants=plants)

# Method for redirecting to add plant page
# Loads and displays all plants for the current user
@app.route('/add_plant', methods=['GET'])
@login_required
def add_plant_page():
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    return render_template('add_plant.html', plants=plants)

# Method for redirecting to the add first plant page
# Does NOT load and display all plants. There are no plants available yet
@app.route('/add_first_plant', methods=['GET'])
@login_required
def add_first_plant_page():
    return render_template('add_first_plant.html', plants=None)

# Function to return the current user info
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  

# Function for a current user to log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if not user:
            # If username does not exist, prevent login and display below message 
            error = 'Invalid username. Try again or add a new profile'
            return render_template('login.html', error=error)
        # If user exists, login and redirect to main page
        login_user(user)
        return redirect('/')
    else:
        return render_template('login.html')
    
# Function to create a new user profile    
@app.route('/new_login', methods=['GET', 'POST'])
def new_login():      
    # If user already exists, log them in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Collect username and email for profile
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        remember_me = request.form.get('remember_me')

        # Checks if user already exists. If not, create new user profile
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if not user:
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=remember_me)
            return redirect('/')
        # If user exists, log them in without creating duplicate account
        login_user(user)
        return redirect('/')

    # Method for redirected to page
    return render_template('new_login.html')

# Function to log the current user out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# Function will check all profiles for plants that are overdue for watering.
# Users with overdue plants will be emailed a list of the plants that need water
def notification():
    with app.app_context():
        users = User.query.all()
        for user in users:

            need_water = []
            plants = Plant.query.filter_by(user_id=user.id).all()
            today = datetime.today().date()
            for plant in plants:
                plant.next_watering = plant.last_watered + timedelta(days=plant.days_between_watering)
                
                if today >= plant.next_watering:
                    need_water.append(plant.name)

            if need_water:
                plants_need_water = ', '.join(need_water)
                message = Message('Notification', sender='plant.tracker.notification@gmail.com', recipients=[f'{user.email}'])
                message.body = f'The following plants need water!\n\n{plants_need_water}'
                mail.send(message)
            

# Configure the scheduler to run the task once a day at a specific time
scheduler = APScheduler()
scheduler.add_job(func=notification, trigger='cron', hour=9, minute=0, id='email notification')

# Start the scheduler
scheduler.init_app(app)
scheduler.start()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
