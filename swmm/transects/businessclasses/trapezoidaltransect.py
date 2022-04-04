from swmm.transects.businessclasses.epa_swmm import Transect


class TrapezoidalTransect(object):
    def __init__(self, name, bottom_width, height, left_slope, right_slope, roughness):
        self.name = name
        self.bottom_width = bottom_width
        self.height = height
        self.left_slope = left_slope
        self.right_slope = right_slope
        self.roughness = roughness

    # def create_transect(self):
    #     first_station_of_bottom_width = self.left_slope * self.height
    #     top_width = first_station_of_bottom_width + self.bottom_width + self.right_slope * self.height
    #
    #     transect = Transect()
    #     transect.name = self.name
    #     transect.n_left = str(self.roughness)
    #     transect.n_right = str(self.roughness)
    #     transect.n_channel = str(self.roughness)
    #     transect.overbank_left = '0'
    #     transect.overbank_right = str(top_width)
    #
    #     first_station = ('0', str(self.height))
    #     second_station = (str(first_station_of_bottom_width), '0')
    #     third_station = (str(first_station_of_bottom_width + self.bottom_width), '0')
    #     fourth_station = (str(top_width), str(self.height))
    #
    #     transect.stations.append(first_station)
    #     transect.stations.append(second_station)
    #     transect.stations.append(third_station)
    #     transect.stations.append(fourth_station)
    #     return transect

    def create_transect(self):
        first_station_of_bottom_width = self.left_slope * self.height
        top_width = first_station_of_bottom_width + self.bottom_width + self.right_slope * self.height

        transect = Transect()
        transect.name = self.name
        transect.n_left = str(self.roughness)
        transect.n_right = str(self.roughness)
        transect.n_channel = str(self.roughness)
        transect.overbank_left = '0'
        transect.overbank_right = str(top_width)

        first_station = (str(self.height), '0')
        second_station = ('0', str(first_station_of_bottom_width))
        third_station = ('0', str(first_station_of_bottom_width + self.bottom_width))
        fourth_station = (str(self.height), str(top_width))

        transect.stations.append(first_station)
        transect.stations.append(second_station)
        transect.stations.append(third_station)
        transect.stations.append(fourth_station)
        return transect