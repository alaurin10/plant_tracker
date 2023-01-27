from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from config import DevelopmentConfig



app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.secret_key = 'stuff'
db = SQLAlchemy(app)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days_between_watering = db.Column(db.Integer, nullable=False)
    last_watered = db.Column(db.Date, nullable=False)
    next_watering = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Plant {self.name}>'

@app.route('/', methods=['GET', 'POST']) 
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
        
    plants = Plant.query.all()
    for plant in plants:
        plant.next_watering = plant.last_watered + timedelta(days=plant.days_between_watering)
    return render_template('index.html', plants=plants)

@app.route('/add_first_plant', methods=['POST'])
def add_first_plant():
    name = request.form['name']
    last_watered = datetime.strptime(request.form['last_watered'], '%Y-%m-%d')
    days_between_watering = request.form['days_between_watering']
    new_plant = Plant(name=name, last_watered=last_watered, days_between_watering=days_between_watering)
    db.session.add(new_plant)
    db.session.commit() 
    return redirect(url_for('add_plant_page'))

@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    if request.method == 'POST':
        name = request.form['name']
        last_watered = datetime.strptime(request.form['last_watered'], '%Y-%m-%d')
        days_between_watering = request.form['days_between_watering']
        new_plant = Plant(name=name, last_watered=last_watered, days_between_watering=days_between_watering)
        db.session.add(new_plant)
        db.session.commit() 
        return redirect(url_for('add_plant_page'))
    else:
        plants = Plant.query.all()
        return render_template('add_plant.html', plants=plants)


@app.route('/delete_plant/<int:id>', methods=['GET', 'POST'])
def delete_plant(id):
    if request.method == 'POST':
        plant = Plant.query.get(id)
        db.session.delete(plant)
        db.session.commit()
        return redirect(url_for('delete_plant_page'))
    else:
        plant = Plant.query.get(id)
        return render_template('delete_plant.html', plant=plant)

@app.route('/water/<int:id>')
def water_plant(id):
    plant = Plant.query.get(id)
    plant.last_watered = datetime.now().date()
    db.session.commit()
    return redirect('/')
    

@app.route('/delete_plant', methods=['GET'])
def delete_plant_page():
    plants = Plant.query.all()
    return render_template('delete_plant.html', plants=plants)

@app.route('/add_plant', methods=['GET'])
def add_plant_page():
    plants = Plant.query.all()
    return render_template('add_plant.html', plants=plants)


@app.route('/add_first_plant', methods=['GET'])
def add_first_plant_page():
    return render_template('add_first_plant.html', plants=None)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
