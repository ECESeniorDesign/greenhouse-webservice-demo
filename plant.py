import lazyrecord
import datetime
import json
import urllib2

plant_database = "localhost:4000"

class Plant(lazyrecord.Base):
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
        "mature_on": lazyrecord.date,
        "slot_id": int,
        "plant_database_id": int,
    }

    __validates__ = {
        "slot_id": lambda slot_id: slot_id in (1, 2)
    }

    @classmethod
    def for_slot(Plant, slot_id):
        try:
            return Plant.find_by(slot_id=slot_id)
        except lazyrecord.RecordNotFound:
            # Probably want a better sentinel object
            return None

    @classmethod
    def from_json(Plant, json_object):
        plant = Plant(**json_object)
        plant.plant_database_id = json_object["id"]
        plant.mature_on = datetime.date.today() + datetime.timedelta(json_object["maturity"])
        return plant

    @classmethod
    def from_database(Plant):
        response = urllib2.urlopen("http://{}/api/plants".format(plant_database))
        plant_list = json.load(response)
        plants = [Plant.from_json(plant) for plant in plant_list]
        return plants

    @classmethod
    def from_database_with_id(Plant, plant_database_id):
        response = urllib2.urlopen("http://{}/api/plants/{}".format(plant_database, plant_database_id))
        plant = json.load(response)
        return Plant.from_json(plant)
