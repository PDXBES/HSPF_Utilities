import copy
import math


class Subbasin(object):
    def __init__(self, hspf, name):
        self.hspf = hspf
        self.forest_code = None
        self.grass_code = None
        self.perlnds = copy.deepcopy(hspf.perlnds)
        self.implnds = copy.deepcopy(hspf.implnds)
        self.connectivity_tables = hspf.connectivity_table
        self.land_use = hspf.land_use
        self.soil = hspf.soil
        self.connectivity = hspf.connectivity
        self.emgaats_area = 0
        self.total_area = 0
        self.total_impervious_area = 0
        self.total_effective_impervious_area = 0
        self.total_pervious_area = 0
        self.subbasin_name = name
        self.outlet_surface_flow = None
        self.outlet_inter_flow = None
        self.outlet_base_flow = None
        self.surfaceflow_area_factor = 1
        self.interflow_area_factor = 1
        self.baseflow_area_factor = 1
        self.soil_areas = dict(zip(self.soil.keys(), len(self.soil)*[0]))
        pass

    def find_forest_code(self):
        for pervious_cover_code in self.hspf.hspf_perv_cover.keys():
            if self.hspf.hspf_perv_cover[pervious_cover_code] == "Forest":
                self.forest_code = pervious_cover_code

    def find_grass_code(self):
        for pervious_cover_code in self.hspf.hspf_perv_cover.keys():
            if self.hspf.hspf_perv_cover[pervious_cover_code] == "Grass":
                self.grass_code = pervious_cover_code

    def code_to_implnd_perlnd_area_new(self, o_code, area, predeveloped=False, include_impervious=True):
        if area > 0:
            code = o_code
            perlnd_group_code = code - code % self.hspf.base_codes["Other"]
            code = code - perlnd_group_code
            soil_code = code - code % self.hspf.base_codes["Soils"]
            code = code - soil_code
            connectivity_code = code - code % self.hspf.base_codes["Connectivity"]
            code = code - connectivity_code
            land_use_code = code - code % self.hspf.base_codes["Land_Use"]
            code = code - land_use_code
            imp_cover_code = code - code % self.hspf.base_codes["Impervious_Cover"]
            code = code - imp_cover_code
            perv_cover_code = code - code % self.hspf.base_codes["Pervious_Cover"]
            code = code - perv_cover_code
            slope_code = code - code % self.hspf.base_codes["Slope"]

            self.soil_areas[soil_code] += area

            hspf_soil_id = int(self.hspf.soil[soil_code][0] + self.hspf.perlnd_family[int(perlnd_group_code)][0])
            hspf_imp_cover_id = self.hspf.imp_cover[imp_cover_code][0]
            hspf_implnd_group_id = int(self.hspf.perlnd_family[int(perlnd_group_code)][0])
            land_use = self.land_use[land_use_code]
            connectivity_table = self.connectivity[connectivity_code][0]
            try:
                imp_connectivity = self.connectivity_tables[self.connectivity_tables['Land_Use'] == land_use][connectivity_table].values[0] #landuse -> row and # connectivity table -> column
            except:
                pass
            hspf_perv_cover_id = self.hspf.perv_cover[perv_cover_code][0]
            hspf_slope_id = self.hspf.slope[slope_code][0]

            if predeveloped:
                self.pervious_area_to_perlnd(area, self.forest_code, hspf_slope_id, hspf_soil_id)
#                self.pervious_area_to_perlnd(area/2, self.grass_code, hspf_slope_id, hspf_soil_id)
            else:
                if self.hspf.hspf_imp_cover[hspf_imp_cover_id][0:4] != "NONE":
                    self.impervious_area_to_perlnd_implnd(area, hspf_slope_id, hspf_soil_id,
                                                          hspf_imp_cover_id, hspf_implnd_group_id, imp_connectivity, include_impervious)
                else:
                    self.pervious_area_to_perlnd(area, hspf_perv_cover_id, hspf_slope_id, hspf_soil_id)

    def pervious_area_to_perlnd(self, area, hspf_perv_cover_id, hspf_slope_id, hspf_soil_id):
        self.total_area += area
        self.total_pervious_area += area
        try:
            perlnd = [perlnd for perlnd in self.perlnds
                      if perlnd.hspf_soil_id == hspf_soil_id and
                      perlnd.hspf_cover_id == hspf_perv_cover_id and
                      perlnd.hspf_slope_id == hspf_slope_id][0]
        except:
            pass
        perlnd.area += area

    def impervious_area_to_perlnd_implnd(self, area, hspf_slope_id, hspf_soil_id, hspf_imp_cover_id, hspf_implnd_group_id, imp_connectivity, include_impervious):
        effective_impervious_area = area * imp_connectivity
        pervious_area = area * (1 - imp_connectivity)
        self.total_area += effective_impervious_area
        self.total_impervious_area += area
        self.total_effective_impervious_area += effective_impervious_area
        if hspf_imp_cover_id == self.hspf.hspf_imp_cover_id["Bldg"]:
            implnd = [implnd for implnd in self.implnds
                      if implnd.hspf_cover_id == hspf_imp_cover_id and
                         implnd.group_id == hspf_implnd_group_id][0]
        else:
            implnd = [implnd for implnd in self.implnds
                      if implnd.hspf_cover_id == hspf_imp_cover_id and
                      implnd.hspf_slope_id == hspf_slope_id and
                      implnd.group_id == hspf_implnd_group_id][0]
        if include_impervious:
            implnd.area += effective_impervious_area
        self.pervious_area_to_perlnd(pervious_area, 3, hspf_slope_id, hspf_soil_id)

