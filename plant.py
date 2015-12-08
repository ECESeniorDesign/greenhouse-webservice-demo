import lazyrecord

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
        return Plant.all()
