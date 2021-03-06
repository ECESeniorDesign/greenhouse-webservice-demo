from flask import Flask, render_template, request, session, url_for, redirect
from models import Plant, SensorDataPoint
from presenters import PlantDataPresenter
import sqlite3
import datetime
app = Flask(__name__)
DATABASE = "/tmp/demo.db"
DEBUG = True
SECRET_KEY = "development key"
USERNAME = "admin"
PASSWORD = "password"
app.config.from_object(__name__)
import eventlet
eventlet.monkey_patch()
from flask_socketio import SocketIO
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')
import time
from threading import Thread
thread = None
import random
from contextlib import closing
import sys
import os
import lazy_record

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def background_thread():
    sun = [25, 25]
    water = [20, 15]
    pH = [8.1, 6.2]
    humidity = [0.67, 0.71]
    while True:
        time.sleep(10)
        for i in range(2):
            sun[i] += random.randint(-5, 5)
            sun[i] = min(max(sun[i], 0), 100)
            water[i] += random.randint(-5, 5)
            water[i] = min(max(water[i], 0), 100)
            humidity[i] = random.random()
            pH[i] = random.random() * 14
        plants = [Plant.for_slot(1, False), Plant.for_slot(2, False)]
        for index, plant in enumerate(plants):
            plant.sensor_data_points.build(sensor_name="light",
                                           sensor_value=sun[index]).save()
            plant.sensor_data_points.build(sensor_name="water",
                                           sensor_value=water[index]).save()
            plant.sensor_data_points.build(sensor_name="humidity",
                                           sensor_value=humidity[index]).save()
            plant.sensor_data_points.build(sensor_name="acidity",
                                           sensor_value=pH[index]).save()
        socketio.emit('data-update', True, namespace="/plants")

@app.route("/debug")
def console():
    import pdb
    pdb.set_trace()
    return redirect(url_for('home'))

@app.route("/")
def home():
    plants = [(Plant.for_slot(1, False), 1), (Plant.for_slot(2, False), 2)]
    return render_template('home.html', plants=plants)

@app.route("/plants/", methods=['POST'])
def create_plant():
    plant = Plant.from_database_with_id(request.form["plant_database_id"])
    plant.slot_id = request.form["slot_id"]
    plant.save()
    return redirect(url_for('home'))

@app.route("/plants/new")
def new_plant():
    plants = Plant.from_database()
    return render_template("select_plant.html", plants=plants,
        slot_id=request.args.get("slot_id"))

@app.route("/plants/<id>")
def your_plant(id):
    plant = Plant.for_slot(id)

    now = datetime.datetime.today()
    total = (plant.mature_on - plant.created_at).days
    remaining = (plant.mature_on - now).days
    assert total >= remaining
    return render_template('your_plant.html',
    # adjust from database values
        sun_bar=SunBar(plant.light, plant.light_ideal, plant.light_tolerance),
        water_bar=WaterBar(plant.water, plant.water_ideal, plant.water_tolerance),
        maturity_dial=MaturityDial(remaining, total),
        pH=VitalInfo("pH", plant.acidity, plant.acidity_ideal, plant.acidity_tolerance,
                     "0.1f", pH_correction),
        humidity=VitalInfo("Humidity", plant.humidity, plant.humidity_ideal,
                           plant.humidity_tolerance, "0.1%", lambda *_: None),
        plant=plant)

@app.route("/plants/<id>/settings")
def edit_plant(id):
    plant = Plant.for_slot(id)
    return render_template("edit_plant.html", plant=plant)

@app.route("/plants/<id>/logs")
def log_plant(id):
    plant = Plant.for_slot(id)
    return render_template("plant_logs.html", plant=plant)

@app.route("/plants/<id>", methods=["DELETE"])
def delete_plant(id):
    plant = Plant.for_slot(id)
    plant.destroy()
    return redirect(url_for('home'))

class MaturityDial(object):
    def __init__(self, remaining, total):
        self.value = remaining
        self.min_value = 2*remaining - total
        self.max_value = 2*remaining
        self.mature = remaining <= 0

class BaseBar(object):
    bar_class = ""

    def __init__(self, current, ideal, tolerance):
        # normalize values so that ideal is 50%
        self.current = ((float(current) * 50) / ideal)
        self.ideal = 50
        # TODO normalize so that the tolerance bands are at 20% & 80%
        self.tolerance = ((float(tolerance) * 50) / ideal)
        # FIXME there might be a bug here
        self.within_tolerance = tolerance >= abs(ideal - current)
        self.over_ideal = self.current > self.ideal
        if self.current > self.ideal + self.tolerance:
            self.bar_width = self.ideal + self.tolerance
            error_width = self.current - self.ideal - self.tolerance
        elif self.current > self.ideal:
            self.bar_width = self.current
            error_width = 0
        elif self.current < self.ideal - self.tolerance:
            self.bar_width = self.current
            error_width = self.ideal - self.tolerance - self.current
        else:
            self.bar_width = self.current
            error_width = 0
        # need to keep the progress bar from overfilling
        # by ensuring that it never goes over 100%
        self.error_width = min(error_width, 100 - self.bar_width)

class SunBar(BaseBar):
    bar_class = "progress-bar-sun"
    icon = "fa fa-sun-o"

class WaterBar(BaseBar):
    icon = "wi wi-raindrop"

class VitalInfo(object):
    def __init__(self, name, current, ideal, tolerance, format, correction):
        self.name = name
        # The 0.001 is to account for floating issues where effectively equal
        # numbers don't compare as expected
        self.within_tolerance = tolerance >= abs(ideal - current) - 0.001
        self.formatted_value = "{0:{format}}".format(current, format=format)
        self.formatted_ideal_value = "{0:{format}}".format(ideal,
            format=format)
        self.formatted_tolerance = "{0:{format}}".format(tolerance,
            format=format)
        # If there is no corrective action to suggest, don't say anything
        self.correction = correction(current, ideal, tolerance) or ""

def pH_correction(current, ideal, tolerance):
    if current > ideal:
        return "Add a teaspoon of white vinegar to the base of the plant."

@socketio.on("request-data", namespace="/plants")
def send_data_to_client(slot_id):
    plant = Plant.for_slot(slot_id, False)
    if plant is None:
        return
    with app.test_request_context('/plants'):
        new_template = render_template('_vitals.html',
            sun_bar=SunBar(plant.light, plant.light_ideal, plant.light_tolerance),
            water_bar=WaterBar(plant.water, plant.water_ideal,
                plant.water_tolerance),
            pH=VitalInfo("pH", plant.acidity, plant.acidity_ideal,
                plant.acidity_tolerance, "0.1f", pH_correction),
            humidity=VitalInfo("Humidity", plant.humidity, plant.humidity_ideal,
                plant.humidity_tolerance, "0.1%", lambda *_: None))
    socketio.emit('new-data', {
        'new-page': new_template
    }, namespace="/plants/{}".format(plant.slot_id), broadcast=False)

@socketio.on("request-chart", namespace="/plants")
def send_chart_data(slot_id):
    plant = Plant.for_slot(slot_id, False)
    if plant is None:
        return
    presenter = PlantDataPresenter(plant)
    socketio.emit('ideal-chart-data', {
        'chart-content': presenter.ideal_chart_data()
    }, namespace="/plants/{}".format(plant.slot_id), broadcast=False)
    socketio.emit('history-chart-data', {
        'chart-content': presenter.history_chart_data()
    }, namespace="/plants/{}".format(plant.slot_id), broadcast=False)

def seed():
    Plant(
        name="Cactus",
        photo_url="http://homeguides.sfgate.com/DM-Resize/"
                  "photos.demandstudios.com/getty/article/"
                  "150/17/skd191046sdc_XS.jpg?w=442&h=442&keep_ratio=1",
        water_ideal=57.0,
        water_tolerance=30.0,
        light_ideal=50.0,
        light_tolerance=10.0,
        acidity_ideal=9.0,
        acidity_tolerance=1.0,
        humidity_ideal=0.2,
        humidity_tolerance=0.1,
        mature_on=datetime.datetime(2016, 1, 10),
        slot_id=1,
        plant_database_id=1).save()
    Plant(
        name="Turnip",
        photo_url="http://homeguides.sfgate.com/DM-Resize/"
                  "photos.demandstudios.com/getty/article/"
                  "30/254/skd286804sdc_XS.jpg?w=442&h=442&keep_ratio=1",
        mature_on = datetime.datetime(2016, 1, 15),
        water_ideal = 15.0,
        water_tolerance = 5.0,
        light_ideal = 25.0,
        light_tolerance = 10.0,
        acidity_ideal = 7.0,
        acidity_tolerance = 0.8,
        humidity_ideal = 0.5,
        humidity_tolerance = 0.1,
        slot_id=2,
        plant_database_id=2).save()

if __name__ == '__main__':
    try:
        lazy_record.connect_db(app.config['DATABASE'])
        bg = Thread(target=background_thread)
        bg.daemon = True
        bg.start()
        socketio.run(app, debug=True)
    except:
        lazy_record.close_db()