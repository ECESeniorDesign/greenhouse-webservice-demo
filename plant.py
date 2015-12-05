import lazyrecord

class Plant(lazyrecord.Base):
    __attributes__ = [
        "name", "photo_url", "water_ideal", "water_tolerance", "light_ideal",
        "light_tolerance", "acidity_ideal", "acidity_tolerance", "humidity_ideal",
        "humidity_tolerance", "mature_on"
    ]
