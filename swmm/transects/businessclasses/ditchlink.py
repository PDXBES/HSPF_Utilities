from shapely.geometry import Point, LineString


class DitchLink(object):
    def __init__(self, parent_link_name, link_name, us_node, ds_node):
        self.parent_link_name = parent_link_name
        self.link_name = link_name
        self.us_node = us_node
        self.ds_node = ds_node

        self.us_node_name = self.us_node.node_name
        self.ds_node_name = self.ds_node.node_name
        self.us_ie_ft = self.us_node.overflow_elev_ft
        self.ds_ie_ft = self.ds_node.overflow_elev_ft
        self.cross_section_id = 1
        self.link_flow_type = 'D'
        self.link_symbology = 'DT'

        self.height = None
        self.geometry = None

    def get_maximum_height(self):
        if self.us_node.height > self.ds_node.height:
            max_height = self.us_node.height
        else:
            max_height = self.ds_node.height
        return max_height

    def get_geometry(self):
        point_geometry = [self.us_node.geometry, self.ds_node.geometry]
        geometry = LineString(point_geometry)
        return geometry

    def get_dict(self):
        link_dict = {"parent_link_name": self.parent_link_name,
                     "link_name": self.link_name,
                     "us_node_name": self.us_node_name,
                     "ds_node_name": self.ds_node_name,
                     "us_ie_ft": self.us_ie_ft,
                     "ds_ie_ft": self.ds_ie_ft,
                     "cross_section_id": self.cross_section_id,
                     "link_flow_type": self.link_flow_type,
                     "link_symbology": self.link_symbology,
                     "height": self.height,
                     "geometry": self.geometry}
        return link_dict
