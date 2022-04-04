from hspf.businessclasses.subbasin import Subbasin
import math

class ExplicitSubbasin(Subbasin):
    def __init__(self, hspf, name):
        super().__init__(hspf, name)
        self.soil_slope_area_lookup = {}
        self.forest_code = None
        self.grass_code = None
        self.area_type = "Bldg"

    def find_grass_code(self):
        for pervious_cover_code in self.hspf.hspf_perv_cover.keys():
            if self.hspf.hspf_perv_cover[pervious_cover_code] == "Grass":
                self.grass_code = pervious_cover_code

    def find_forest_code(self):
        for pervious_cover_code in self.hspf.hspf_perv_cover.keys():
            if self.hspf.hspf_perv_cover[pervious_cover_code] == "Forest":
                self.forest_code = pervious_cover_code

    def create_soil_slope_area_lookup(self):
        for soil_code in self.hspf.hspf_soil.keys():
            for slope_code in self.hspf.hspf_slope.keys():
                key = (soil_code, slope_code)
                area = 0
                self.soil_slope_area_lookup[key] = area

    def code_to_soil_slope_area_explicit_impervious(self, o_code, area):
        if area > 0:
            code = o_code
            soil1_code = code - code % self.hspf.base_codes["Other"]
            code = code - soil1_code
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

            hspf_soil_id = self.hspf.soil[soil_code][0] + soil1_code/1000000
            hspf_slope_id = self.hspf.slope[slope_code][0]
            try:
                self.soil_slope_area_lookup[(hspf_soil_id, hspf_slope_id)] += area
            except:
                print("Not found " + str(hspf_soil_id) + " " + str(hspf_slope_id))

    def explicit_impervious_area_to_perlnd_implnd(self, area, area_factor, con_area, dsi_area, dsv_area, dry_area,
                                                  eco_area, rng_area, predeveloped=False, include_impervious=True):
        for hspf_slope_id in self.hspf.hspf_slope.keys():
            for hspf_soil_id in self.hspf.hspf_soil.keys():
                hspf_imp_cover_id = self.hspf.hspf_imp_cover_id[self.area_type]
                soil_slope_area = self.soil_slope_area_lookup[(hspf_soil_id, hspf_slope_id)]
                soil_slope_area_factor = soil_slope_area / area
                if soil_slope_area > 0:
                    if predeveloped:
                        self.pervious_area_to_perlnd(con_area * soil_slope_area_factor,
                                                     self.forest_code,
                                                     hspf_slope_id,
                                                     hspf_soil_id)
                        # self.pervious_area_to_perlnd(con_area * soil_slope_area_factor/2,
                        #                              self.grass_code,
                        #                              hspf_slope_id,
                        #                              hspf_soil_id)
                        self.pervious_area_to_perlnd(dsi_area * soil_slope_area_factor,
                                                     self.forest_code,
                                                     hspf_slope_id,
                                                     hspf_soil_id)
                        # self.pervious_area_to_perlnd(con_area * soil_slope_area_factor/2,
                        #                              self.grass_code,
                        #                              hspf_slope_id,
                        #                              hspf_soil_id)
                    else:
                        self.impervious_area_to_perlnd_implnd(con_area*soil_slope_area_factor,
                                                              hspf_slope_id,
                                                              hspf_soil_id,
                                                              hspf_imp_cover_id,
                                                              area_factor,
                                                              include_impervious)
                        self.impervious_area_to_perlnd_implnd(dsi_area*soil_slope_area_factor,
                                                              hspf_slope_id,
                                                              hspf_soil_id,
                                                              hspf_imp_cover_id,
                                                              area_factor,
                                                              include_impervious)
                    self.pervious_area_to_perlnd(dsv_area*soil_slope_area_factor,
                                                 self.forest_code,
                                                 hspf_slope_id,
                                                 hspf_soil_id)
                    self.pervious_area_to_perlnd(dry_area*soil_slope_area_factor,
                                                 self.forest_code,
                                                 hspf_slope_id,
                                                 hspf_soil_id)
                    self.pervious_area_to_perlnd(eco_area*soil_slope_area_factor,
                                                 self.forest_code,
                                                 hspf_slope_id,
                                                 hspf_soil_id)
                    self.pervious_area_to_perlnd(rng_area*soil_slope_area_factor,
                                                 self.forest_code,
                                                 hspf_slope_id,
                                                 hspf_soil_id)

    # def impervious_area_to_perlnd_implnd(self, area, hspf_slope_id, hspf_soil_id, hspf_imp_cover_id, imp_connectivity):
    #     effective_impervious_area = area * imp_connectivity
    #     pervious_area = area * (1 - imp_connectivity)
    #     self.total_area += effective_impervious_area
    #     self.total_impervious_area += area
    #     self.total_effective_impervious_area += effective_impervious_area
    #     if hspf_imp_cover_id == self.hspf.hspf_imp_cover_id["Bldg"]:
    #         implnd = [implnd for implnd in self.implnds
    #                   if implnd.hspf_cover_id == hspf_imp_cover_id][0]
    #     else:
    #         implnd = [implnd for implnd in self.implnds
    #                   if implnd.hspf_cover_id == hspf_imp_cover_id and
    #                   implnd.hspf_slope_id == hspf_slope_id][0]
    #     implnd.area += effective_impervious_area
    #     self.pervious_area_to_perlnd(pervious_area, 3, hspf_slope_id, hspf_soil_id)
