from shapely.geometry import Point, LineString, shape


class DitchNode(object):
    def __init__(self, parent_link_name, transect_name, node_name):
        self.parent_link_name = parent_link_name
        self.transect_name = transect_name
        self.node_name = node_name
        self.node_symbology = 'wwj'
        self.top_type = 'DualDrainage'

        self.ground_elev_ft = None
        self.x = None
        self.y = None
        self.overflow_elev_ft = None
        self.height = None
        self.geometry = None

    # def find_overflow_elevation(self):
    #     overflow_elev_ft = None
    #     for station_data in self.station_data:
    #         if station_data.Final_Code not in ['CROWN', 'EAC']:
    #             if overflow_elev_ft is None:
    #                 overflow_elev_ft = station_data.Elevation
    #             elif overflow_elev_ft < station_data.Elevation:
    #                 overflow_elev_ft = station_data.Elevation
    #     if overflow_elev_ft is None:
    #         raise Exception("height was not found")
    #     return overflow_elev_ft
    #
    # def calculate_height(self):
    #     height = None
    #     max_elev = None
    #     for station_data in self.station_data:
    #         if max_elev is None:
    #             max_elev = station_data.Elevation
    #         elif max_elev < station_data.Elevation:
    #             max_elev = station_data.Elevation
    #     if max_elev is not None:
    #         height = max_elev - self.ground_elev_ft
    #     else:
    #         raise Exception("max_elev was not found")
    #     return height

    def get_geometry(self):
        xy = (self.x, self.y)
        geometry = Point(xy)
        return geometry

    def get_dict(self):
        node_dict = {"parent_link_name": self.parent_link_name,
                     "node_name": self.node_name,
                     "node_symbology": self.node_symbology,
                     "top_type": self.top_type,
                     "ground_elev_ft": self.overflow_elev_ft,
                     "thalweg_elev_ft": self.ground_elev_ft,
                     "height": self.height,
                     "geometry": self.geometry}
        return node_dict