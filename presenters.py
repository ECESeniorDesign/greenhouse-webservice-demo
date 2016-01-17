class PlantDataPresenter(object):

    def __init__(self, plant):
        self.plant = plant

    def ideal_chart_data(self):
        # Light only, for now (might have to add group_by to lazy_record)
        within_tolerance_count = len(list(self.plant.sensor_data_points.light().where(
            "sensor_value >= ? AND sensor_value <= ?",
            self.plant.light_ideal - self.plant.light_tolerance,
            self.plant.light_ideal + self.plant.light_tolerance)))
        total_count = len(list(self.plant.sensor_data_points.light()))
        out_tolerance_count = total_count - within_tolerance_count
        return [{
                    "label": "Out of Tolerance",
                    "value": out_tolerance_count,
                    "color":"#F7464A",
                    "highlight": "#FF5A5E",
                },
                {
                    "label": "Ideal",
                    "value": within_tolerance_count,
                    "color": "#46BFBD",
                    "highlight": "#5AD3D1",
                }]
