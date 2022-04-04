import pandas as pd
import numpy as np
import sys

class Outlet(object):
    """SWMM node where unrouted HSPF flow is sent"""
    def __init__(self, outlet_name, perlnd_ids, implnd_ids):
        self.name = outlet_name
        self.perlnd_ids = perlnd_ids
        self.implnd_ids = implnd_ids
        self.surface_flow_areas = None
        self.inter_flow_areas = None
        self.base_flow_areas = None
        self.surface_flow = None
        self.inter_flow = None
        self.base_flow = None
        self.total_flow = None

    def calculate_surface_flow_areas(self, subbasins):
        surface_flow_subbasins = [subbasin for subbasin in subbasins if subbasin.outlet_surface_flow == self.name]
        outlet_areas = []
        for subbasin in surface_flow_subbasins:
            subbasin_areas = [perlnd.area * subbasin.surfaceflow_area_factor for perlnd in subbasin.perlnds]
            subbasin_areas += [implnd.area for implnd in subbasin.implnds] # Give option to scale impervious area as well?
            # subbasin_areas += [implnd.area * subbasin.surfaceflow_area_factor for implnd in subbasin.implnds]
            outlet_areas.append(subbasin_areas)
        outlet_area_array = np.array(outlet_areas)
        self.surface_flow_areas = np.sum(outlet_area_array, axis=0)

    def calculate_inter_flow_areas(self, subbasins):
        inter_flow_subbasins = [subbasin for subbasin in subbasins if subbasin.outlet_inter_flow == self.name]
        outlet_areas = []
        for subbasin in inter_flow_subbasins:
            subbasin_areas = [perlnd.area * subbasin.interflow_area_factor for perlnd in subbasin.perlnds]
            outlet_areas.append(subbasin_areas)
        outlet_area_array = np.array(outlet_areas)
        self.inter_flow_areas = np.sum(outlet_area_array, axis=0)

    def calculate_base_flow_areas(self, subbasins):
        baseflow_subbasins = [subbasin for subbasin in subbasins if subbasin.outlet_base_flow == self.name]
        outlet_areas = []
        for subbasin in baseflow_subbasins:
            subbasin_areas = [perlnd.area * subbasin.baseflow_area_factor for perlnd in subbasin.perlnds]
            outlet_areas.append(subbasin_areas)
        outlet_area_array = np.array(outlet_areas)
        self.base_flow_areas = np.sum(outlet_area_array, axis=0)

    def calculate_surface_flow(self, hru_surface_flow_dataframe):
        outlet_flow_dataframe = hru_surface_flow_dataframe * self.surface_flow_areas
        self.surface_flow = pd.DataFrame(outlet_flow_dataframe.sum(axis=1))
        self.surface_flow['node'] = self.name

    def calculate_inter_flow(self, hru_inter_flow_dataframe):
        outlet_flow_dataframe = hru_inter_flow_dataframe * self.inter_flow_areas
        self.inter_flow = pd.DataFrame(outlet_flow_dataframe.sum(axis=1))
        self.inter_flow['node'] = self.name

    def calculate_base_flow(self, hru_base_flow_dataframe):
        outlet_flow_dataframe = hru_base_flow_dataframe * self.base_flow_areas
        self.base_flow = pd.DataFrame(outlet_flow_dataframe.sum(axis=1))
        self.base_flow['node'] = self.name

    def calculate_total_flow(self):
        if self.base_flow is not None and not self.base_flow.empty and \
           self.inter_flow is not None and not self.inter_flow.empty and \
           self.surface_flow is not None and not self.surface_flow.empty:
            self.total_flow = pd.DataFrame(self.base_flow[0] + self.inter_flow[0] + self.surface_flow[0])
        elif self.surface_flow is not None and not self.surface_flow.empty and self.inter_flow is not None and not self.inter_flow.empty:
            self.total_flow = pd.DataFrame(self.base_flow[0] + self.inter_flow[0] + self.surface_flow[0])
        elif self.surface_flow is not None and not self.surface_flow.empty and self.base_flow is not None and not self.base_flow.empty:
            self.total_flow = pd.DataFrame(self.inter_flow[0] + self.surface_flow[0])
        elif self.inter_flow is not None and not self.surface_flow.empty and self.base_flow is not None and not self.base_flow.empty:
            self.total_flow = pd.DataFrame(self.base_flow[0] + self.inter_flow[0])
        elif self.surface_flow is not None and not self.surface_flow.empty:
            self.total_flow = pd.DataFrame(self.surface_flow[0])
        elif self.inter_flow is not None and not self.inter_flow.empty:
            self.total_flow = pd.DataFrame(self.inter_flow[0])
        elif self.base_flow is not None and not self.base_flow.empty:
            self.total_flow = pd.DataFrame(self.base_flow[0])
        else:
            print("No Flow")
            sys.exit()
        self.total_flow['node'] = self.name
