from flask import Flask, render_template, request, session
app = Flask(__name__)
import eventlet
eventlet.monkey_patch()
from flask_socketio import SocketIO
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')
import time
from threading import Thread
thread = None
import random

ideal_water = 45
water_tolerance = 5
ideal_sun = 30
sun_tolerance = 10
ideal_pH = 7
pH_tolerance = 0.2
ideal_humidity = 0.72
humidity_tolerance = 0.07

def background_thread():
    while True:
        time.sleep(10)
        global sun, water, pH, humidity
        sun += random.randint(-5, 5)
        water += random.randint(-5, 5)
        humidity = random.random()
        with app.test_request_context('/your-plant'):
            new_template = render_template('vitals.html',
                sun_bar=SunBar(sun, ideal_sun, sun_tolerance),
                water_bar=WaterBar(water, ideal_water, water_tolerance),
                pH=VitalInfo("pH", pH, ideal_pH, pH_tolerance, "0.1f",
                             pH_correction),
                humidity=VitalInfo("Humidity", humidity, ideal_humidity,
                                   humidity_tolerance, "0.1%", lambda *_: None))
        socketio.emit('new-data', {
            'new-page': new_template
        })

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/your-plant/")
def your_plant():
    global sun, water, pH, humidity, remaining, total

    remaining = float(session.get("remaining", 85))
    total = float(session.get("total", 100))
    sun = int(session.get("sun", 40))
    water = int(session.get("water", 35))
    pH = float(session.get("pH", 8.1))
    humidity = float(session.get("humidity", 0.67))

    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()

    assert total > remaining
    return render_template('your_plant.html',
        sun_bar=SunBar(sun, ideal_sun, sun_tolerance),
        water_bar=WaterBar(water, ideal_water, water_tolerance),
        maturity_dial=MaturityDial(remaining, total),
        pH=VitalInfo("pH", pH, ideal_pH, pH_tolerance, "0.1f",
                     pH_correction),
        humidity=VitalInfo("Humidity", humidity, ideal_humidity,
                           humidity_tolerance, "0.1%", lambda *_: None))


class MaturityDial(object):
    def __init__(self, remaining, total):
        self.value = remaining
        self.min_value = 2*remaining - total
        self.max_value = 2*remaining

class BaseBar(object):
    bar_class = ""

    def __init__(self, current, ideal, tolerance):
        # normalize values so that ideal is 50%
        self.current = ((float(current) * 50) / ideal)
        self.ideal = 50
        self.tolerance = ((float(tolerance) * 50) / ideal)

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
        # The 0.001 is to account for floating issues where effectively equal numbers don't compare as expected
        self.within_tolerance = tolerance >= abs(ideal - current) - 0.001
        self.formatted_value = "{0:{format}}".format(current, format=format)
        self.formatted_ideal_value = "{0:{format}}".format(ideal, format=format)
        self.formatted_tolerance = "{0:{format}}".format(tolerance, format=format)
        # If there is no corrective action to suggest, don't say anything
        self.correction = correction(current, ideal, tolerance) or ""

def pH_correction(current, ideal, tolerance):
    if current > ideal:
        return "Add a teaspoon of white vinegar to the base of the plant."

if __name__ == '__main__':
    socketio.run(app, debug=True)
