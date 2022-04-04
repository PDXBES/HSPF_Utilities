from swmm.transects.businessclasses.epa_swmm import Transect


class NaturalChannelTransect(object):
    def __init__(self, name, parent_link_name, xsname, cross_section_data):
        self.name = name
        self.parent_link_name = parent_link_name
        self.xsname = xsname
        self.cross_section_data = list(cross_section_data)
        self.left_overbank_point = self.cross_section_data[0].Point
        self.right_overbank_point = self.cross_section_data[-1].Point
        self.left_overbank_roughness = 0.035
        self.roughness_channel = 0.035
        self.right_overbank_roughness = 0.035

    def create_transect(self):
        transect = Transect()
        transect.name = self.name
        transect.n_channel = str(self.roughness_channel)
        transect.n_left = str(self.left_overbank_roughness)
        transect.n_right = str(self.right_overbank_roughness)
        for station_number, station_data in enumerate(self.cross_section_data):
            if station_data.Point == self.left_overbank_point:
                transect.overbank_left = str(station_data.Station)

            elif station_data.Point == self.right_overbank_point:
                transect.overbank_right = str(station_data.Station)

            station = (str(station_data.Elevation), str(station_data.Station))
            transect.stations.append(station)
        return transect

    def find_thalweg_station_data(self):
        thalweg_station = None
        min_elev = None
        for station_data in self.cross_section_data:
            if min_elev is None:
                min_elev = station_data.Elevation
                thalweg_station = station_data
            elif min_elev > station_data.Elevation:
                min_elev = station_data.Elevation
                thalweg_station = station_data
        if thalweg_station is None:
            raise Exception("Thalweg not found: " + self.name)
        return thalweg_station