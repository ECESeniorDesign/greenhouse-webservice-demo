from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/your-plant/")
def your_plant():
    remaining = float(request.args.get("remaining", 85))
    total = float(request.args.get("total", 100))
    sun=int(request.args.get("sun", 40))
    water=int(request.args.get("water", 35))
    pH = float(request.args.get("pH", 8.1))
    humidity = float(request.args.get("humidity", 0.67))
    ideal_water = 45
    water_tolerance = 5
    ideal_sun = 30
    sun_tolerance = 10
    ideal_pH = 7
    pH_tolerance = 0.2
    ideal_humidity = 0.72
    humidity_tolerance = 0.07
    assert total > remaining
    return render_template('your_plant.html',
        sun_bar=SunBar(sun, ideal_sun, sun_tolerance),
        water_bar=WaterBar(water, ideal_water, water_tolerance),
        maturity_dial=MaturityDial(remaining, total),
        pH=VitalInfo("pH", pH, ideal_pH, pH_tolerance, "0.1f", pH_corrective_action),
        humidity=VitalInfo("Humidity", humidity, ideal_humidity, humidity_tolerance, "0.1%", lambda *_: None))


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
    def __init__(self, name, current, ideal, tolerance, format, corrective_action):
        self.name = name
        # The 0.001 is to account for floating issues where effectively equal numbers don't compare as expected
        self.within_tolerance = tolerance >= abs(ideal - current) - 0.001
        self.formatted_value = "{0:{format}}".format(current, format=format)
        self.formatted_ideal_value = "{0:{format}}".format(ideal, format=format)
        self.formatted_tolerance = "{0:{format}}".format(tolerance, format=format)
        # If there is no corrective action to suggest, don't say anything
        self.corrective_action = corrective_action(current, ideal, tolerance) or ""

def pH_corrective_action(current, ideal, tolerance):
    if current > ideal:
        return "Add a teaspoon of white vinegar to the base of the plant."

if __name__ == '__main__':
    app.run(debug=True)
