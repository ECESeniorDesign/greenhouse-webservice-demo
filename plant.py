import lazyrecord
import datetime

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
    def from_database(Plant):
        # Hardcoded plant until we can get a new one
        return [
            Plant(
                name="Onion",
                photo_url="https://pbs.twimg.com/profile_images/595950387003166720/4BpRufhU.jpg",
                mature_on = datetime.date(2016, 2, 15),
                water_ideal = 10.0,
                water_tolerance = 5.0,
                light_ideal = 35.0,
                light_tolerance = 10.0,
                acidity_ideal = 7.0,
                acidity_tolerance = 0.8,
                humidity_ideal = 0.6,
                humidity_tolerance = 0.1,
                plant_database_id = 3)
        ]

    @classmethod
    def from_database_with_id(Plant, plant_database_id):
        return Plant(
                name="Onion",
                photo_url="https://pbs.twimg.com/profile_images/595950387003166720/4BpRufhU.jpg",
                mature_on = datetime.date(2016, 2, 15),
                water_ideal = 10.0,
                water_tolerance = 5.0,
                light_ideal = 35.0,
                light_tolerance = 10.0,
                acidity_ideal = 7.0,
                acidity_tolerance = 0.8,
                humidity_ideal = 0.6,
                humidity_tolerance = 0.1,
                plant_database_id = 3)
