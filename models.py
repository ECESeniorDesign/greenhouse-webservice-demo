import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__))), "lazy_record"))
import lazy_record
from lazy_record.associations import *
import datetime
import json
import urllib2

plant_database = "localhost:4000"

@belongs_to("plant")
class SensorDataPoint(lazy_record.Base):
    # Later add temperature, conductivity...
    __validates__ = {
        "sensor_name": lambda name: name in (
            "water", "light", "humidity", "acidity"
        )
    }
    __attributes__ = {
        "sensor_name": str,
        "sensor_value": float,
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
        "mature_on": lazy_record.date,
        "slot_id": int,
        "plant_database_id": int,
    }

    __validates__ = {
        "slot_id": lambda slot_id: slot_id in (1, 2)
    }

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
