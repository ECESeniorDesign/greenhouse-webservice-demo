class PlantDataPresenter(object):

    def __init__(self, plant):
        self.plant = plant

    def ideal_chart_data(self):
        # Light only, for now (might have to add group_by to lazy_record)
        within_tolerance_count = len(self.plant.sensor_data_points.light().where(
            "sensor_value >= ? AND sensor_value <= ?",
            self.plant.light_ideal - self.plant.light_tolerance,
            self.plant.light_ideal + self.plant.light_tolerance))
        total_count = len(self.plant.sensor_data_points.light())
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

    def history_chart_data(self):
        # For some reason, it is getting 2 new points per cycle
        num_points = 8
        light_data = [point.sensor_value for point in self.plant.sensor_data_points.light()][-num_points:]
        return  {
                    "labels": [""] * num_points,
                    "datasets": [
                                    {
                                        'fillColor': "rgba(220,220,220,0.2)",
                                        'strokeColor': "rgba(220,220,220,1)",
                                        'pointColor': "rgba(220,220,220,1)",
                                        'pointStrokeColor': "#fff",
                                        'data': light_data,
                                    }
                                ]
                }
