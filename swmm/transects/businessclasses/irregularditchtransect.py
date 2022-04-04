from swmm.transects.businessclasses.epa_swmm import Transect


class IrregularDitchTransect(object):
    def __init__(self, name, parent_link_name, xsname, cross_section_data, roughness_channel, roughness_asphalt):
        self.name = name
        self.parent_link_name = parent_link_name
        self.xsname = xsname
        self.cross_section_data = list(cross_section_data)
        self.roughness_channel = roughness_channel
        self.roughness_asphalt = roughness_asphalt
        self.ditch_on_left = False
        self.stations = None
        self.thalweg_station = None
        self.ground_elev_ft = None

    def create_transect(self):
        transect = Transect()
        transect.name = self.name
        transect.n_channel = str(self.roughness_channel)
        number_of_stations = len(self.cross_section_data)
        stations_numeric = []
        for station_number, station_data in enumerate(self.cross_section_data):
            if station_number == 0:
                if station_data.Final_Code is not None:
                    if station_data.Final_Code in ['EAC', 'CROWN', 'GUT']:
                        transect.n_left = str(self.roughness_asphalt)
                    else:
                        transect.n_left = str(self.roughness_channel)
                        transect.overbank_left = str(station_data.Station)
                        self.ditch_on_left = True
                else:
                    print("Final_Code is none for xs:" + self.name)
                    transect.n_left = str(self.roughness_channel)
            if self.ditch_on_left:
                if transect.overbank_right == '0' and station_data.Final_Code in ['EAC', 'AC', 'CROWN', 'GUT']:
                    transect.overbank_right = str(station_data.Station)
                    transect.n_right = str(self.roughness_asphalt)
            elif station_number == number_of_stations-1:
                transect.n_right = str(self.roughness_channel)
                transect.overbank_right = str(station_data.Station)
            else:
                if station_number > 0 and transect.overbank_left == '0' and station_data.Final_Code in ['EAC']:
                    transect.overbank_left = str(station_data.Station)
                    transect.n_left = str(self.roughness_asphalt)
            stations_numeric.append((station_data.Station, station_data.Elevation, station_data.Final_Code))

        self.stations = self.remove_stations_that_are_not_effective(stations_numeric, transect)

        for station_numeric in self.stations:
            station = (str(station_numeric[1]), str(station_numeric[0]))
            transect.stations.append(station)
        return transect

    def remove_stations_that_are_not_effective(self, stations_numeric, transect):
        if self.ditch_on_left:
            previous_station = None
            final_stations_numeric = []
            for index, station_numeric in enumerate(reversed(stations_numeric)):
                if previous_station is None:
                    previous_station = station_numeric
                elif station_numeric[1] > previous_station[1] and station_numeric[2] not in ['TOPS', 'TOES', 'THALWEG']:
                    if float(transect.overbank_right) > previous_station[0]:
                        transect.overbank_right = str(station_numeric[1])
                else:
                    final_stations_numeric.append(previous_station)
                previous_station = station_numeric
            final_stations_numeric.append(stations_numeric[0])
            final_stations_numeric.reverse()
        else:
            previous_station = None
            final_stations_numeric = []
            for index, station_numeric in enumerate(stations_numeric):
                if previous_station is None:
                    previous_station = station_numeric
                elif station_numeric[1] > previous_station[1] and station_numeric[2] not in ['TOPS', 'TOES', 'THALWEG']:
                    if float(transect.overbank_right) > previous_station[0]:
                        transect.overbank_right = str(station_numeric[1])
                else:
                    final_stations_numeric.append(previous_station)
                previous_station = station_numeric
            final_stations_numeric.append(stations_numeric[-1])
        return final_stations_numeric

    def find_overflow_elevation(self):
        overflow_elev_ft = None
        for station_data in self.stations:
            if station_data[2] not in ['CROWN', 'AC', 'GUT', 'EAC']:
                if overflow_elev_ft is None:
                    overflow_elev_ft = station_data[1]
                elif overflow_elev_ft < station_data[1]:
                    overflow_elev_ft = station_data[1]
        if overflow_elev_ft is None:
            raise Exception("height was not found")
        return overflow_elev_ft

    def calculate_height(self):
        height = None
        max_elev = None
        for station_data in self.stations:
            if max_elev is None:
                max_elev = station_data[1]
            elif max_elev < station_data[1]:
                max_elev = station_data[1]
        if max_elev is not None:
            height = max_elev - self.ground_elev_ft
        else:
            raise Exception("max_elev was not found")
        return height

    def find_thalweg_station_data(self):
        thalweg_station = None
        min_elev = None
        for station_data in self.cross_section_data:
            if station_data.Final_Code not in ['EAC', 'CROWN', 'AC', 'GUT']:
                if min_elev is None:
                    min_elev = station_data.Elevation
                    thalweg_station = station_data
                elif min_elev > station_data.Elevation:
                    min_elev = station_data.Elevation
                    thalweg_station = station_data
        if thalweg_station is None:
            raise Exception("Thalweg not found: " + self.name)
        return thalweg_station


