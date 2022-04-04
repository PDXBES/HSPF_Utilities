from swmm.transects.dataio.transect_dataio import TransectDataIo
from swmm.transects.businessclasses.trapezoidaltransect import TrapezoidalTransect
from swmm.transects.businessclasses.streettransect import StreetTransect
from swmm.transects.businessclasses.irregularditchtransect import IrregularDitchTransect
from swmm.transects.businessclasses.naturalchanneltransect import NaturalChannelTransect
#from transects.businessclasses.ditchnode import DitchNode
#from transects.businessclasses.ditchlink import DitchLink
#import geopandas as gpd


class SWMMTransects(object):
    def __init__(self, transect_dataio):
        self.transect_dataio: TransectDataIo = transect_dataio
        self.trapezoid_transects = []
        self.irregular_ditch_transects = []
        self.natural_channel_transects = []
        self.street_transects = []
        self.ditchnodes = []
        self.ditchlinks = []

    def create_trapezoid_transects(self):
        trapezoids_data = self.transect_dataio.trapezoidal_transect_df.itertuples()
        for trapezoid_data in trapezoids_data:
            name = trapezoid_data.LinkName
            bottom_width = trapezoid_data.BottomWidthFt
            height = trapezoid_data.MaxDepthFt
            left_slope = trapezoid_data.LeftSideSlope
            right_slope = trapezoid_data.RightSideSlope
            roughness = trapezoid_data.Roughness
            trapezoidal_transect = TrapezoidalTransect(name, bottom_width, height, left_slope, right_slope,
                                                       roughness).create_transect()
            if trapezoid_data.Use == 'YES':
                self.trapezoid_transects.append(trapezoidal_transect)

    def create_street_transects(self):
        streets_data = self.transect_dataio.street_transect_df.itertuples()
        for street_data in streets_data:
            street_transect = StreetTransect(street_data).create_transect()
            if street_data.Use == 'YES':
                self.street_transects.append(street_transect)

    def create_irregular_ditch_transects(self):
        irregular_ditches_data = self.transect_dataio.surveyed_ditch_transect_df.itertuples()
        roughness_channel = 0.035 #TODO should not be hardwired
        roughness_asphalt = 0.01 #TODO should not be hardwired
        for irregular_ditch_data in irregular_ditches_data:
            parent_link_name = irregular_ditch_data.Parent_Link_Name
            xs_name = irregular_ditch_data.XS_Name
            number_of_transects_used = self.get_number_of_transects_used_on_link(self.transect_dataio.surveyed_ditch_transect_df, parent_link_name)
            if number_of_transects_used > 1:
                name = parent_link_name + "_" + str(xs_name)
            else:
                name = parent_link_name
            irregular_transect_data = self.get_transect_xs_data(self.transect_dataio.surveyed_ditch_xs_transect_df, parent_link_name, xs_name)
            irregular_ditch_transect = IrregularDitchTransect(name, parent_link_name, xs_name, irregular_transect_data,
                                                              roughness_channel, roughness_asphalt).create_transect()
            if irregular_ditch_data.Use == 'YES':
                self.irregular_ditch_transects.append(irregular_ditch_transect)

    def create_natural_channel_transects(self):
        natural_channels_data = self.transect_dataio.natural_channel_transect_df.itertuples()
        roughness_channel = 0.035 #TODO should not be hardwired
        for natural_channel_data in natural_channels_data:
            parent_link_name = natural_channel_data.Parent_Link_Name
            xs_name = natural_channel_data.XS_Name
            number_of_transects_used = self.get_number_of_transects_used_on_link(
                self.transect_dataio.natural_channel_transect_df, parent_link_name)
            if number_of_transects_used > 1:
                name = parent_link_name + "_" + str(xs_name)
            else:
                name = parent_link_name

            natural_channel_transect_data = self.get_transect_xs_data(self.transect_dataio.natural_channel_xs_transect_df, parent_link_name, xs_name)
            natural_channel_xs = NaturalChannelTransect(name, parent_link_name, xs_name, natural_channel_transect_data)
            natural_channel_xs.roughness_channel = roughness_channel
            natural_channel_transect = natural_channel_xs.create_transect()
            if natural_channel_data.Use == 'YES':
                self.natural_channel_transects.append(natural_channel_transect)

    def get_all_transects(self):
        transects = self.street_transects + self.trapezoid_transects + self.irregular_ditch_transects + self.natural_channel_transects
        return transects

    def get_transect_xs_data(self, xs_df, parent_link_name, xs_name):
        all_xs_data_for_parent_link = xs_df[xs_df['Parent_Link_Name'] == parent_link_name]
        transect_xs_data_df = all_xs_data_for_parent_link[all_xs_data_for_parent_link['XS_Name'] == xs_name]
        transect_xs_data = transect_xs_data_df.itertuples()
        return transect_xs_data

    def get_number_of_transects_used_on_link(self, xs_df, parent_link_name):
        all_xs_data_for_parent_link_df = xs_df[xs_df['Parent_Link_Name'] == parent_link_name]
        all_xs_data_for_parent_link = list(all_xs_data_for_parent_link_df.itertuples())
        number_of_xs_used = 0
        for xs in all_xs_data_for_parent_link:
            if xs.Use == 'YES':
                number_of_xs_used += 1
        return number_of_xs_used


    # def create_irregular_ditch_nodes(self):
    #     ditchnodedicts = []
    #     irregular_ditches_data = self.transect_dataio.surveyed_ditch_transect_df.itertuples()
    #     roughness_channel = 0.035 #TODO should not be hardwired
    #     roughness_asphalt = 0.01 #TODO should not be hardwired
    #     for irregular_ditch_data in irregular_ditches_data:
    #         parent_link_name = irregular_ditch_data.Parent_Link_Name
    #         xs_name = irregular_ditch_data.XS_Name
    #         name = parent_link_name + "_" + str(xs_name)
    #
    #         irregular_transect_data = self.get_transect_xs_data(self.transect_dataio.surveyed_ditch_xs_transect_df, parent_link_name, xs_name)
    #         irregular_ditch_transect = IrregularDitchTransect(name, parent_link_name, xs_name, irregular_transect_data,
    #                                                           roughness_channel, roughness_asphalt)
    #         irregular_ditch_transect.create_transect()
    #         irregular_ditch_transect.thalweg_station = irregular_ditch_transect.find_thalweg_station_data()
    #         irregular_ditch_transect.ground_elev_ft = irregular_ditch_transect.thalweg_station.Elevation
    #         ditchnode = DitchNode(parent_link_name, xs_name, name)
    #         ditchnode.ground_elev_ft = irregular_ditch_transect.thalweg_station.Elevation
    #         ditchnode.overflow_elev_ft = irregular_ditch_transect.find_overflow_elevation()
    #         ditchnode.height = irregular_ditch_transect.calculate_height()
    #         ditchnode.x = irregular_ditch_transect.thalweg_station.Easting
    #         ditchnode.y = irregular_ditch_transect.thalweg_station.Northing
    #         ditchnode.geometry = ditchnode.get_geometry()
    #         self.ditchnodes.append(ditchnode)
    #         if irregular_ditch_data.Use == 'YES':
    #             ditchnodedicts.append(ditchnode.get_dict())
    #     node_gdf = gpd.GeoDataFrame(ditchnodedicts, geometry='geometry')
    #     return node_gdf
    #
    # def create_irregular_ditch_links(self):
    #     ditchlinkdicts = []
    #     irregular_ditches_data = self.transect_dataio.surveyed_ditch_transect_df.itertuples()
    #     us_transect_name = None
    #     us_node = None
    #     ds_node = None
    #     for irregular_ditch_data in irregular_ditches_data:
    #         parent_link_name = irregular_ditch_data.Parent_Link_Name
    #         xs_name = irregular_ditch_data.XS_Name
    #         name = parent_link_name + "_" + str(xs_name)
    #         if us_transect_name is None:
    #             us_transect_name = name
    #             us_node = next((node for node in self.ditchnodes if node.node_name == us_transect_name), None)
    #         else:
    #             ds_node = next((node for node in self.ditchnodes if node.node_name == name), None)
    #             link = DitchLink(parent_link_name, name, us_node, ds_node)
    #             link.height = link.get_maximum_height()
    #             link.geometry = link.get_geometry()
    #             self.ditchlinks.append(link)
    #             ditchlinkdicts.append(link.get_dict())
    #             us_transect_name = name
    #             us_node = ds_node
    #     link_gdf = gpd.GeoDataFrame(ditchlinkdicts, geometry='geometry')
    #     return link_gdf