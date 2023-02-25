from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from config import DevelopmentConfig



app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.secret_key = 'stuff'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'alaurin10@gmail.com'
app.config['MAIL_PASSWORD'] = 'cvuqiscxthbdrccs'

mail = Mail(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    plants = db.relationship('Plant', backref='user', lazy=True)
  

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days_between_watering = db.Column(db.Integer, nullable=False)
    last_watered = db.Column(db.Date, nullable=False)
    next_watering = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Plant {self.name}>'
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))      
 
@app.route('/', methods=['GET', 'POST']) 
@login_required
def index():
    if request.method == 'POST':
        name = request.form['name']
        days_between_watering = request.form['days_between_watering']
        last_watered = datetime.now()
        next_watering = last_watered + timedelta(days=int(days_between_watering))

        plant = Plant(name=name, days_between_watering=days_between_watering, last_watered=last_watered, next_watering=next_watering)
        db.session.add(plant)
        db.session.commit()

        return redirect(url_for('index'))
        
    # plants = Plant.query.all()
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    for plant in plants:
        plant.next_watering = plant.last_watered + timedelta(days=plant.days_between_watering)
    return render_template('index.html', plants=plants)

@app.route('/add_first_plant', methods=['POST'])
@login_required
def add_first_plant():
    name = request.form['name']
    last_watered = datetime.strptime(request.form['last_watered'], '%Y-%m-%d')
    days_between_watering = request.form['days_between_watering']
    new_plant = Plant(name=name, last_watered=last_watered, days_between_watering=days_between_watering, user_id=current_user.id)
    db.session.add(new_plant)
    db.session.commit() 
    return redirect(url_for('add_plant_page'))

@app.route('/add_plant', methods=['GET', 'POST'])
@login_required
def add_plant():
    if request.method == 'POST':
        name = request.form['name']
        last_watered = datetime.strptime(request.form['last_watered'], '%Y-%m-%d')
        days_between_watering = request.form['days_between_watering']
        new_plant = Plant(name=name, last_watered=last_watered, days_between_watering=days_between_watering, user_id=current_user.id)
        db.session.add(new_plant)
        db.session.commit() 
        return redirect(url_for('add_plant_page'))
    else:
        # plants = Plant.query.all()
        plants = Plant.query.filter_by(user_id=current_user.id).all()
        if not plants:
            # return redirect(url_for('index'))
            return render_template('add_first_plant.html', plants=None)
        return render_template('add_plant.html', plants=plants)


@app.route('/delete_plant/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_plant(id):
    if request.method == 'POST':
        # plant = Plant.query.get(id)
        plant = Plant.query.filter_by(user_id=current_user.id, id=id).first()
        db.session.delete(plant)
        db.session.commit()
        return redirect(url_for('delete_plant_page'))
    else:
        # plant = Plant.query.get(id)
        plant = Plant.query.filter_by(user_id=current_user.id, id=id).first()
        return render_template('delete_plant.html', plant=plant)

@app.route('/water/<int:id>')
@login_required
def water_plant(id):
    # plant = Plant.query.get(id)
    plant = Plant.query.filter_by(user_id=current_user.id, id=id).first()
    plant.last_watered = datetime.now().date()
    db.session.commit()
    return redirect('/')
    

@app.route('/delete_plant', methods=['GET'])
@login_required
def delete_plant_page():
    # plants = Plant.query.all()
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    if not plants:
        return redirect(url_for('index'))
    return render_template('delete_plant.html', plants=plants)

@app.route('/add_plant', methods=['GET'])
@login_required
def add_plant_page():
    # plants = Plant.query.all()
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    return render_template('add_plant.html', plants=plants)


@app.route('/add_first_plant', methods=['GET'])
@login_required
def add_first_plant_page():
    return render_template('add_first_plant.html', plants=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if not user:
            # Create a new user if the username doesn't exist
            error = 'Invalid username. Try again or add a new profile'
            return render_template('login.html', error=error)
        login_user(user)
        return redirect('/')
    else:
        return render_template('login.html')
    
@app.route('/new_login', methods=['GET', 'POST'])
def new_login():      
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        remember_me = request.form.get('remember_me')

        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if not user:
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=remember_me)
            return redirect('/')

    return render_template('new_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


def my_task():
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
                message = Message('Notification', sender='alaurin10@gmail.com', recipients=[f'{user.email}'])
                message.body = f'The following plants need water!\n\n{plants_need_water}'
                mail.send(message)
            

scheduler = APScheduler()
# Configure the scheduler to run the task once a day at a specific time
scheduler.add_job(func=my_task, trigger='cron', hour=9, minute=0, id='email notification')

# Start the scheduler
scheduler.init_app(app)
scheduler.start()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
