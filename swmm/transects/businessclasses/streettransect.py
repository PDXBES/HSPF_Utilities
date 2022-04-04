from swmm.transects.businessclasses.epa_swmm import Transect
import math


class StreetTransect(object):
    def __init__(self, street_data):
        self.name = street_data.LinkName
        self.left_curb_height_ft = street_data.LeftCurbHeightFt
        self.crown_height_ft = street_data.CrownHeightFt
        self.right_curb_height_ft = street_data.RightCurbHeightFt
        self.left_lane_width = street_data.LeftLaneWidthFt
        self.right_lane_width = street_data.RightLaneWidthFt
        self.roughness = street_data.Roughness

    def create_transect(self):
        transect = Transect()
        transect.name = str(self.name)
        transect.n_left = str(self.roughness)
        transect.n_right = str(self.roughness)
        transect.n_channel = str(self.roughness)
        transect.overbank_left = '0'
        transect.overbank_right = str(self.left_lane_width + self.right_lane_width)
        if (not math.isnan(self.left_lane_width) and self.left_lane_width > 0) and (not math.isnan(self.right_lane_width) and self.right_lane_width > 0):
            transect = self.full_street(transect)
        elif math.isnan(self.left_lane_width) or self.left_lane_width == 0:
            transect = self.right_half_street(transect)
        elif math.isnan(self.right_lane_width) or self.right_lane_width == 0:
            transect = self.left_half_street(transect)
        else:
            print("invalid street transect: " + str(self.name))
        return transect

    def full_street(self, transect):
        if self.left_curb_height_ft != 0:
            top_curb_left_station = (str(self.left_curb_height_ft), '0')
            transect.stations.append(top_curb_left_station)
        bottom_curb_left_station = ('0', '0')
        transect.stations.append(bottom_curb_left_station)
        crown_station = (str(self.crown_height_ft), str(self.left_lane_width))
        transect.stations.append(crown_station)
        bottom_curb_right_station = ('0', str(self.right_lane_width + self.left_lane_width))
        transect.stations.append(bottom_curb_right_station)
        if self.right_curb_height_ft != 0:
            top_curb_right_station = (str(self.right_curb_height_ft), str(self.right_lane_width + self.left_lane_width))
            transect.stations.append(top_curb_right_station)
        return transect

    def right_half_street(self, transect):
        crown_station = (str(self.crown_height_ft), '0')
        transect.stations.append(crown_station)
        bottom_curb_right_station = ('0', str(self.right_lane_width))
        transect.stations.append(bottom_curb_right_station)
        if self.right_curb_height_ft != 0:
            top_curb_right_station = (str(self.right_curb_height_ft), str(self.right_lane_width))
            transect.stations.append(top_curb_right_station)
        return transect

    def left_half_street(self, transect):
        if self.left_curb_height_ft != 0:
            top_curb_left_station = (str(self.left_curb_height_ft), '0')
            transect.stations.append(top_curb_left_station)
        bottom_curb_left_station = ('0', '0')
        transect.stations.append(bottom_curb_left_station)
        crown_station = (str(self.crown_height_ft), str(self.left_lane_width))
        transect.stations.append(crown_station)    
        return transect

