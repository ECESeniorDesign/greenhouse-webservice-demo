import sys
import os
import lazy_record
from lazy_record.associations import *
from lazy_record.validations import *
import datetime
import json
import urllib2

plant_database = "localhost:4000"

@belongs_to("plant")
class SensorDataPoint(lazy_record.Base):
    # Later add temperature, conductivity...
    __validates__ = {
        "sensor_name": lambda record: record.sensor_name in (
            "water",
            "light",
            "humidity",
            "acidity",
        )
    }
    __attributes__ = {
        "sensor_name": str,
        "sensor_value": float,
    }
    __scopes__ = {
        "water": lambda query: query.where(sensor_name="water"),
        "light": lambda query: query.where(sensor_name="light"),
        "humidity": lambda query: query.where(sensor_name="humidity"),
        "acidity": lambda query: query.where(sensor_name="acidity"),
    }

    @classmethod
    def record(SensorDataPoint, name, value, slot_id):
        """
        Records a piece of sensor data for a slot. Returns True on success,
        False if there is not plant in that slot (where the data is not saved)
        """
        plant = Plant.for_slot(slot_id)
        if plant:
            point = SensorDataPoint(sensor_name=name,
                                    sensor_value=value,
                                    plant_id=plant.id)
            point.save()
            return True
        else:
            return False

@has_many("sensor_data_points")
class Plant(lazy_record.Base):
    __attributes__ = {
        "name": str,
        "photo_url": str,
        "water_ideal": float,
        "water_tolerance": float,
        "light_ideal": float,
        "light_tolerance": float,
        "acidity_ideal": float,
        "acidity_tolerance": float,
        "humidity_ideal": float,
        "humidity_tolerance": float,
        "mature_on": lazy_record.datetime,
        "slot_id": int,
        "plant_database_id": int,
    }

    __validates__ = {
        "slot_id": lambda record: unique("slot_id")(record) and \
                                  record.slot_id in (1, 2),
    }

    @property
    def light(self):
        point = self.sensor_data_points.light().last()
        if point:
            return point.sensor_value
        else:
            return 0

    def light_values(self):
        return [point.sensor_value
                for point in self.sensor_data_points.light()][-10:]

    @property
    def water(self):
        point = self.sensor_data_points.water().last()
        if point:
            return point.sensor_value
        else:
            return 0

    def water_values(self):
        return [point.sensor_value
                for point in self.sensor_data_points.water()][-10:]

    @property
    def humidity(self):
        point = self.sensor_data_points.humidity().last()
        if point:
            return point.sensor_value
        else:
            return 0

    def humidity_values(self):
        return [point.sensor_value
                for point in self.sensor_data_points.humidity()][-10:]

    @property
    def acidity(self):
        point = self.sensor_data_points.acidity().last()
        if point:
            return point.sensor_value
        else:
            return 0

    def acidity_values(self):
        return [point.sensor_value
                for point in self.sensor_data_points.acidity()][-10:]

    @classmethod
    def for_slot(Plant, slot_id, raise_if_not_found=True):
        try:
            return Plant.find_by(slot_id=slot_id)
        except lazy_record.RecordNotFound:
            if raise_if_not_found:
                raise

    @classmethod
    def from_json(Plant, json_object):
        plant_database_id = json_object["id"]
        del json_object["id"]
        del json_object["inserted_at"]
        del json_object["updated_at"]
        plant = Plant(**json_object)
        plant.plant_database_id = plant_database_id
        plant.mature_on = datetime.date.today() + datetime.timedelta(
            json_object["maturity"])
        return plant

    @classmethod
    def from_database(Plant):
        response = urllib2.urlopen("http://{}/api/plants".format(
            plant_database))
        plant_list = json.load(response)
        plants = [Plant.from_json(plant) for plant in plant_list]
        return plants

    @classmethod
    def from_database_with_id(Plant, plant_database_id):
        response = urllib2.urlopen("http://{}/api/plants/{}".format(
            plant_database, plant_database_id))
        plant = json.load(response)
        return Plant.from_json(plant)
