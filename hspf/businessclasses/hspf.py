import csv
import pandas as pd
import numpy as np
from wdmtoolbox import wdmtoolbox
from hspf.businessclasses.implnd import Implnd
from hspf.businessclasses.perlnd import Perlnd
from hspf.businessclasses.outlet import Outlet
from hspf.businessclasses.subbasin import Subbasin
from hspf.businessclasses.explicit_subbasin import ExplicitSubbasin
from typing import Optional, List
from common.conversion_constants import ConversionConstants
import math
import sys


class Hspf(object):
# TODO add command line interface
# TODO add progress bar

    def __init__(self, hspf_data_io):
        self.wdm_file = None
        self.conversion_constants = ConversionConstants()
        self.hru_area_in_acres = 1 #500/43560 #500 sq ft stick to integers to avoid additional rounding errors

        self.start_date_time = "1/1/2020"
        self.stop_date_time = "2/10/2020"
        self.output_timestep_in_minutes = 5  # TODO appsettings
        self.input_timestep_in_minutes = 5  # TODO appsettings
        self.cell_area_sqft = 9  # TODO should not be hardwired move to appsettings
        self.perlnd_surface_flow_base_dsn = 1000  # TODO should not be hardwired move to appsettings
        self.implnd_surface_flow_base_dsn = 2000  # TODO should not be hardwired move to appsettings
        self.perlnd_inter_flow_base_dsn = 3000  # TODO should not be hardwired move to appsettings
        self.perlnd_base_flow_base_dsn = 4000  # TODO should not be hardwired move to appsettings

        self.base_codes = hspf_data_io.read_hspf_input_file_overlay_base_codes()
        self.perlnd_family = hspf_data_io.read_hspf_input_file_overlay_perlnd_group_codes()
        self.soil = hspf_data_io.read_hspf_input_file_overlay_soil_codes()
        self.slope = hspf_data_io.read_hspf_input_file_overlay_slopes_codes()
        self.perv_cover = hspf_data_io.read_hspf_input_file_overlay_pervious_cover_codes()
        self.connectivity = hspf_data_io.read_hspf_input_file_overlay_connectivity_codes()
        self.imp_cover = hspf_data_io.read_hspf_input_file_overlay_impervious_cover_codes()
        self.land_use = hspf_data_io.read_hspf_input_file_overlay_land_use_codes()

        self.connectivity_table = hspf_data_io.read_hspf_input_file_connectivity_tables()

        self.hspf_perv_cover, self.hspf_perv_cover_id = hspf_data_io.read_hspf_input_file_hspf_pervious_cover()

        self.hspf_slope, self.hspf_slope_id = hspf_data_io.read_hspf_input_file_hspf_slope()

        self.hspf_soil, self.hspf_soil_id = hspf_data_io.read_hspf_input_file_hspf_soils()

        self.hspf_imp_cover, self.hspf_imp_cover_id = hspf_data_io.read_hspf_input_file_hspf_impervious_cover()
        self.pwater = hspf_data_io.read_hspf_input_file_pwater()
        self.iwater = hspf_data_io.read_hspf_input_file_iwater()
        self.ftable = hspf_data_io.read_hspf_input_file_ftable()

        self.hru_surface_flow_df: Optional[pd.DataFrame] = None
        self.hru_inter_flow_df: Optional[pd.DataFrame] = None
        self.hru_base_flow_df: Optional[pd.DataFrame] = None

        self.surface_flow_df: Optional[pd.DataFrame] = None
        self.inter_flow_df: Optional[pd.DataFrame] = None
        self.base_flow_df: Optional[pd.DataFrame] = None
        self.flow_df: Optional[pd.DataFrame] = None

        self.subbasins: List[Subbasin] = []
        self.explicit_impervious_area_subbasins: List[Subbasin] = []
        self.node_outlets: List[Outlet] = []
        self.dsns = []
        self.codes = []
        self.perlnds = None
        self.implnds = None

    @staticmethod
    def reverse_dict(dictionary):
        # TODO should move to utility class
        reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
        return reverse_dictionary

    def read_input_file(self, input_file, predevelopment=False, include_impervious=True):  # TODO move to dataio
        with open(input_file) as input_csv:
            reader = csv.reader(input_csv, dialect="excel")

            for row in reader:
                if reader.line_num == 1:
                    self.create_subbasins_from_header(row)
                else:
                    code = int(row[1].replace(',', ''))
                    self.codes.append(code)
                    for count, subbasin in enumerate(self.subbasins, 1):
                        subbasin.find_forest_code()
                        subbasin.find_grass_code()
                        try:
                            area = float(float(row[count+1]) * self.cell_area_sqft)/self.conversion_constants.sqft_per_acre
                        except:
                            print(count)
                        subbasin.code_to_implnd_perlnd_area_new(code, area, predevelopment, include_impervious=include_impervious)

    def read_new_outlet_file(self, outlets): # TODO move to dataio
        with open(outlets) as input_csv:
            reader = csv.reader(input_csv, dialect="excel")
            for row in reader:
                if reader.line_num == 1:
                    pass
                else:
                    subbasin_name = row[0]
                    outlet = row[1]
                    total_area = float(row[2])
                    surfaceflow_area = float(row[3])
                    interflow_area = float(row[4])
                    baseflow_area = float(row[5])
                    try:
                        subbasin = [subbasin for subbasin in self.subbasins if subbasin.subbasin_name == subbasin_name][0]
                    except:
                        print("Subbasin Name not found in overlay" + " " + str(subbasin_name))
                    subbasin.emgaats_area = total_area/self.conversion_constants.sqft_per_acre
                    if subbasin.outlet_surface_flow is None and surfaceflow_area > 0:
                        subbasin.outlet_surface_flow = outlet
                        if surfaceflow_area != total_area:
                            subbasin.surfaceflow_area_factor = surfaceflow_area / total_area
                            print ("Subbasin " + str(subbasin_name) + " surface flow_area: " + str(surfaceflow_area) + " is not the same as total area: " + str(total_area))
                    elif surfaceflow_area > 0:
                        print ("subbasin: " + str(subbasin.subbasin_name) + " has more than 1 surface flow outlet")
                    if subbasin.outlet_inter_flow is None and interflow_area > 0:
                        subbasin.outlet_inter_flow = outlet
                        if interflow_area != total_area:
                            subbasin.interflow_area_factor = interflow_area / total_area
                            print ("Subbasin " + str(subbasin_name) + " interflow_area: " + str(interflow_area) + " is not the same as total area: " + str(total_area))
                    elif interflow_area > 0:
                        print ("subbasin: " + str(subbasin.subbasin_name) + " has more than 1 inter flow outlet")
                    if subbasin.outlet_base_flow is None and baseflow_area > 0:
                        subbasin.outlet_base_flow = outlet
                        if baseflow_area != total_area:
                            subbasin.baseflow_area_factor = baseflow_area/total_area
                            print ("Subbasin " + str(subbasin_name) + " base flow_area: " + str(baseflow_area) + " is not the same as total area: " + str(total_area))
                    elif baseflow_area > 0:
                        print ("subbasin: " + str(subbasin.subbasin_name) + " has more than 1 base flow outlet")

    def create_explicit_impervious_area_subbasins(self, explicit_impervious_area_outlet, input_file, predeveloped=False, include_impervious=False):
        try:
            input_file_df = pd.read_csv(input_file, skipinitialspace=True)
            #input_file_df.LABEL = pd.to_numeric(input_file_df.LABEL.replace({',': ''}, regex=True))
            codes = input_file_df.LABEL
        except:
            print("Could not read explicit area input file")
            return

        try:
            explicit_impervious_area_outlet_df = pd.read_csv(explicit_impervious_area_outlet, skipinitialspace=True)
            explicit_impervious_area_outlet_df.dropna(subset=["suro_outlet",
                                                              "ifwo_outlet",
                                                              "agwo_outlet"],
                                                      how="all",
                                                      inplace=True)
        except:
            print("Could not read explicit area outlet file")
            return

        sorted_explicit_impervious_area_outlet_df = explicit_impervious_area_outlet_df.sort_values(by=['area_name'])
        explicit_outlet_data = sorted_explicit_impervious_area_outlet_df.itertuples()
        for explicit_outlet in explicit_outlet_data:
            area_name = str(explicit_outlet.area_name)
            # outlet_name = str(explicit_outlet.outlet_name)
            subbasin_name = area_name + "_"
            if isinstance(explicit_outlet.suro_outlet, str):
                suro_outlet_name = str(explicit_outlet.suro_outlet)
                subbasin_name += suro_outlet_name + "_"
            else:
                suro_outlet_name = None
            if isinstance(explicit_outlet.ifwo_outlet, str):
                ifwo_outlet_name = str(explicit_outlet.ifwo_outlet)
                subbasin_name += ifwo_outlet_name + "_"
            else:
                ifwo_outlet_name = None
            if isinstance(explicit_outlet.agwo_outlet, str):
                agwo_outlet_name = str(explicit_outlet.agwo_outlet)
                subbasin_name += agwo_outlet_name
            else:
                agwo_outlet_name = None

            # subbasin_name = area_name + "_" + outlet_name

            # try:

            areas = input_file_df[area_name]
            non_zero_areas = areas[areas > 0]
            if not non_zero_areas.empty:
                explicit_subbasin = ExplicitSubbasin(self, subbasin_name)
                explicit_subbasin.find_grass_code()
                explicit_subbasin.find_forest_code()
                explicit_subbasin.create_soil_slope_area_lookup()
                # explicit_subbasin.outlet_surface_flow = outlet_name
                # explicit_subbasin.outlet_base_flow = outlet_name
                # explicit_subbasin.outlet_inter_flow = outlet_name

                explicit_subbasin.outlet_surface_flow = suro_outlet_name
                explicit_subbasin.outlet_base_flow = agwo_outlet_name
                explicit_subbasin.outlet_inter_flow = ifwo_outlet_name

                for row_id in non_zero_areas.index:
                    raster_cells = non_zero_areas[row_id]
                    code = codes[row_id]
                    area = float(int(raster_cells) * self.cell_area_sqft) / self.conversion_constants.sqft_per_acre
                    explicit_subbasin.code_to_soil_slope_area_explicit_impervious(code, area)
                explicit_subbasin.explicit_impervious_area_to_perlnd_implnd(explicit_outlet.area / self.conversion_constants.sqft_per_acre,
                                                                            explicit_outlet.area_factor,
                                                                            explicit_outlet.con_area_sqft / self.conversion_constants.sqft_per_acre,
                                                                            explicit_outlet.dsi_area_sqft / self.conversion_constants.sqft_per_acre,
                                                                            explicit_outlet.dsv_area_sqft / self.conversion_constants.sqft_per_acre,
                                                                            explicit_outlet.dry_area_sqft / self.conversion_constants.sqft_per_acre,
                                                                            explicit_outlet.eco_area_sqft / self.conversion_constants.sqft_per_acre,
                                                                            explicit_outlet.rng_area_sqft / self.conversion_constants.sqft_per_acre,
                                                                            predeveloped,
                                                                            include_impervious
                                                                            )
                self.explicit_impervious_area_subbasins.append(explicit_subbasin)
                print("Added explicit impervious area subbsasin area_name: " + str(area_name) + " suro ifwo agwo outlet_names: " + subbasin_name)
            else:
                print("Explicit area: " + str(area_name) + " has no area overlay input_file")
                # except:
                #     print(str(sys.exc_info()[0]))
                #     sys.exit()

    def create_perlnds(self, perlnd_df):
        perlnds_data = perlnd_df.itertuples()
        perlnds = []
        for perlnd_data in perlnds_data:
            perlnd = Perlnd(self, perlnd_data.Cover, perlnd_data.Slope, perlnd_data.Soil, perlnd_data.Perlnd_Number)
            perlnds.append(perlnd)
        return perlnds

    def create_implnds(self, implnd_df):
        implnds = []
        implnds_data = implnd_df.itertuples()
        for implnd_data in implnds_data:
            implnd = Implnd(self, implnd_data.Cover, implnd_data.Slope, implnd_data.Implnd_Number)
            implnds.append(implnd)
        return implnds

    def implnd_ids(self):
        ids = []
        if self.implnds is None or len(self.implnds) == 0:
            raise Exception('Implnds attribute is none')
        implnds = self.implnds
        for implnd in implnds:
            ids.append(implnd.implnd_id)
        return ids

    def perlnd_ids(self):
        ids = []
        perlnds = self.perlnds
        if self.perlnds is None or len(self.perlnds) == 0:
            raise Exception('Perlnds attribute is none')
        for perlnd in perlnds:
            ids.append(perlnd.perlnd_id)
        return ids

    def create_subbasins_from_header(self, header):
        if len(header) > 3:
            subbasin_names = header[2:]
        else:
            subbasin_names = [header[2]]

        for subbasin_name in subbasin_names:
            subbasin = Subbasin(self, subbasin_name)
            self.subbasins.append(subbasin)

    def create_unique_outlets(self):
        outlets = []
        perlnd_ids = self.perlnd_ids()
        implnd_ids = self.implnd_ids()
        for subbasin in self.subbasins:
            if not subbasin.outlet_surface_flow and not subbasin.outlet_inter_flow and not subbasin.outlet_base_flow:
                print("Area: " + subbasin.subbasin_name + " is not connected to a node")
            else:
                if subbasin.outlet_base_flow is not None:
                    outlets.append(subbasin.outlet_base_flow)
                else:
                    print("Area: " + subbasin.subbasin_name + " base flow is not connected to a node")
                if subbasin.outlet_inter_flow is not None:
                    outlets.append(subbasin.outlet_inter_flow)
                else:
                    print("Area: " + subbasin.subbasin_name + " inter flow is not connected to a node")
                if subbasin.outlet_surface_flow is not None:
                    outlets.append(subbasin.outlet_surface_flow)
                else:
                    print("Area: " + subbasin.subbasin_name + " surface flow is not connected to a node")
        for explicit_subbasin in self.explicit_impervious_area_subbasins:
            if explicit_subbasin.outlet_base_flow is not None:
                outlets.append(explicit_subbasin.outlet_base_flow)
            else:
                print("Explicit Area: " + explicit_subbasin.subbasin_name + " base flow is not connected to a node")
            if explicit_subbasin.outlet_inter_flow is not None:
                outlets.append(explicit_subbasin.outlet_inter_flow)
            else:
                print("Explicit Area: " + explicit_subbasin.subbasin_name + " inter flow is not connected to a node")
            if explicit_subbasin.outlet_surface_flow is not None:
                outlets.append(explicit_subbasin.outlet_surface_flow)
            else:
                print("Explicit Area: " + explicit_subbasin.subbasin_name + " surface flow is not connected to a node")

        unique_outlets = set(outlets)
        for outlet in unique_outlets:
            self.node_outlets.append(Outlet(outlet, perlnd_ids, implnd_ids))
        try:
            self.node_outlets.sort(key=lambda outlet: outlet.name)
        except:
            pass

    def calculate_areas_for_outlets(self):
        if self.subbasins and self.explicit_impervious_area_subbasins:
            all_subbasins = self.subbasins + self.explicit_impervious_area_subbasins
            print("Lumped and Explicit Subbasins")
        elif self.subbasins and not self.explicit_impervious_area_subbasins:
            all_subbasins = self.subbasins
            print("No Explicit Subbasins")
        elif not self.subbasins and self.explicit_impervious_area_subbasins:
            all_subbasins = self.explicit_impervious_area_subbasins
            print("No Lumped Subbasins")
        else:
            print("No Subbasins Program Ended")
            sys.exit()

        for outlet in self.node_outlets:
            outlet.calculate_base_flow_areas(all_subbasins)
            outlet.calculate_inter_flow_areas(all_subbasins)
            outlet.calculate_surface_flow_areas(all_subbasins)

    def calculate_flow_at_each_outlet(self):
        for outlet in self.node_outlets:
            outlet.calculate_base_flow(self.hru_base_flow_df)
            outlet.calculate_inter_flow(self.hru_inter_flow_df)
            outlet.calculate_surface_flow(self.hru_surface_flow_df)
            outlet.calculate_total_flow()

    def surface_flow_dsns(self):
        dsns = []
        for perlnd_id in self.perlnd_ids():
            dsns.append(self.perlnd_surface_flow_base_dsn + perlnd_id)
        for implnd_id in self.implnd_ids():
            dsns.append(self.implnd_surface_flow_base_dsn + implnd_id)
        return dsns

    def inter_flow_dsns(self):
        dsns = []
        for perlnd_id in self.perlnd_ids():
            dsns.append(self.perlnd_inter_flow_base_dsn + perlnd_id)
        return dsns

    def base_flow_dsns(self):
        dsns = []
        for perlnd_id in self.perlnd_ids():
            dsns.append(self.perlnd_base_flow_base_dsn + perlnd_id)
        return dsns

    def create_hru_surface_flow_dataframe(self):
        dsns = self.surface_flow_dsns()
        hru_surfaceflows = []
        for dsn in dsns:
            flow = self.extract_dsn_and_resample(dsn)
            flow = self.filter_flow_based_on_start_and_stop_dates(flow)
            hru_surfaceflows.append(flow)
        self.hru_surface_flow_df = pd.concat(hru_surfaceflows, axis=1)

    def extract_dsn_and_resample(self, dsn):
        flow = wdmtoolbox.extract(self.wdm_file, dsn).fillna(value=0)
        if self.output_timestep_in_minutes is not None:
            flow = flow.resample(str(self.output_timestep_in_minutes) + 'T').mean()
        return flow

    def create_hru_inter_flow_dataframe(self):
        dsns = self.inter_flow_dsns()
        hru_interflows = []
        for dsn in dsns:
            flow = self.extract_dsn_and_resample(dsn)
            flow = self.filter_flow_based_on_start_and_stop_dates(flow)
            hru_interflows.append(flow)
        self.hru_inter_flow_df = pd.concat(hru_interflows, axis=1)

    def create_hru_base_flow_dataframe(self):
        dsns = self.base_flow_dsns()
        hru_baseflows = []
        for dsn in dsns:
            flow = self.extract_dsn_and_resample(dsn)
            flow = self.filter_flow_based_on_start_and_stop_dates(flow)
            hru_baseflows.append(flow)
        self.hru_base_flow_df = pd.concat(hru_baseflows, axis=1)

    def filter_flow_based_on_start_and_stop_dates(self, flow):
        if self.start_date_time is not None and self.stop_date_time is not None:
            flow = flow.loc[self.start_date_time:self.stop_date_time]
        return flow

    def create_outlet_surface_flow_dataframe(self):
        total_flows = []
        for outlet in self.node_outlets:
            total_flows.append(outlet.surface_flow)
        self.surface_flow_df = pd.concat(total_flows, axis=0)
        self.surface_flow_df = self.surface_flow_df.sort_values(by=['Datetime', 'node'])

    def create_outlet_inter_flow_dataframe(self):
        total_flows = []
        for outlet in self.node_outlets:
            total_flows.append(outlet.inter_flow)
        self.inter_flow_df = pd.concat(total_flows, axis=0)
        self.inter_flow_df = self.flow_df.sort_values(by=['Datetime', 'node'])

    def create_outlet_base_flow_dataframe(self):
        total_flows = []
        for outlet in self.node_outlets:
            total_flows.append(outlet.total_flow)
        self.base_flow_df = pd.concat(total_flows, axis=0)
        self.base_flow_df = self.base_flow_df.sort_values(by=['Datetime', 'node'])

    def create_outlet_flow_dataframe(self):
        total_flows = []
        for outlet in self.node_outlets:
            total_flows.append(outlet.total_flow)
        self.flow_df = pd.concat(total_flows, axis=0)
        self.flow_df = self.flow_df.sort_values(by=['Datetime', 'node'])

    def number_of_outlets(self):
        number_of_nodes = int(len(self.node_outlets))
        return number_of_nodes

    def create_flow_df_for_interface_file(self):
        flow_df = self.flow_df.reset_index()
        flow_df[0] = flow_df[0]/self.hru_area_in_acres
        number_of_outlets = self.number_of_outlets()
        non_duplicate_dates = flow_df['Datetime'].drop_duplicates().dt.strftime("%Y %m %d %H %M %S").to_numpy()
        date_times = np.repeat(a=non_duplicate_dates, repeats=number_of_outlets, axis=0)
        reorder_df = pd.DataFrame({'Node': flow_df['node'], 'Datetime': date_times, 'Flow': flow_df[0]})
        return reorder_df

    def create_flow_df_for_interface_file_half_flow(self):
        flow_df = self.flow_df.reset_index()
        flow_df[0] = flow_df[0]/self.hru_area_in_acres/2
        number_of_outlets = self.number_of_outlets()
        non_duplicate_dates = flow_df['Datetime'].drop_duplicates().dt.strftime("%Y %m %d %H %M %S").to_numpy()
        date_times = np.repeat(a=non_duplicate_dates, repeats=number_of_outlets, axis=0)
        reorder_df = pd.DataFrame({'Node': flow_df['node'], 'Datetime': date_times, 'Flow': flow_df[0]})
        return reorder_df

    def create_flow_df_for_interface_file_for_ftable_creation(self):
        flow_df = self.flow_df.reset_index()
        flow_df[0] = flow_df[0] / self.hru_area_in_acres
        begin_date_of_design_storm = "2000-1-2 12:00"
        end_date_of_design_storm = "2000-1-3 12:00"
        max_flow = self.flow_df.copy(deep=True).loc[begin_date_of_design_storm:end_date_of_design_storm]
        maxflow_per_node = max_flow.groupby(['node']).max()
        maxflow_per_node = maxflow_per_node.reset_index()

        flow_df = flow_df.merge(maxflow_per_node, on=['node'])
        flow_df['0'] = flow_df['0_y']
        flow_df = flow_df.drop(columns=['0_y', '0_x'])
        flow_df = flow_df.sort_values(['Datetime', 'node'])

        number_of_outlets = self.number_of_outlets()
        non_duplicate_dates = flow_df['Datetime'].drop_duplicates().dt.strftime("%Y %m %d %H %M %S").to_numpy()
        date_times = np.repeat(a=non_duplicate_dates, repeats=number_of_outlets, axis=0)
        reorder_df = pd.DataFrame({'Node': flow_df['node'], 'Datetime': date_times, 'Flow': flow_df['0']})
        return reorder_df

    # def read_outlet_file(self, outlets):    # TODO move to dataio
    #     with open(outlets) as input_csv:
    #         reader = csv.reader(input_csv, dialect="excel")
    #         for row in reader:
    #             if reader.line_num == 1:
    #                 pass
    #             else:
    #                 subbasin_name = row[0]
    #                 surfaceflow_outlet = row[1]
    #                 interflow_outlet = row[2]
    #                 baseflow_outlet = row[3]
    #                 subbasin = [subbasin for subbasin in self.subbasins if subbasin.subbasin_name == subbasin_name][0]
    #                 subbasin.outlet_surface_flow = surfaceflow_outlet
    #                 subbasin.outlet_inter_flow = interflow_outlet
    #                 subbasin.outlet_base_flow = baseflow_outlet