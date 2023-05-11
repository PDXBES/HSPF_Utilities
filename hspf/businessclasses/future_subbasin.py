from hspf.businessclasses.subbasin import Subbasin
import math


class FutureSubbasin(Subbasin):
    def __init__(self, hspf, name):
        super().__init__(hspf, name)
        self.soil_slope_cover_area_lookup = {}
        self.forest_code = None
        self.grass_code = None
        self.area_type = 'Bldg'
        self.area_check_imp = 0
        self.area_check_perv = 0

    # def find_grass_code(self):
    #     for pervious_cover_code in self.hspf.hspf_perv_cover.keys():
    #         if self.hspf.hspf_perv_cover[pervious_cover_code] == "Grass":
    #             self.grass_code = pervious_cover_code
    #
    # def find_forest_code(self):
    #     for pervious_cover_code in self.hspf.hspf_perv_cover.keys():
    #         if self.hspf.hspf_perv_cover[pervious_cover_code] == "Forest":
    #             self.forest_code = pervious_cover_code

    def create_soil_slope_perv_cover_landuse_connectivity_area_lookup(self):
        for soil_code in self.hspf.hspf_soil.keys():
            for slope_code in self.hspf.hspf_slope.keys():
                for perv_cover_code in self.hspf.hspf_perv_cover.keys():
                    for perlnd_family_code in self.hspf.perlnd_family.values():
                        key = (soil_code, slope_code, perlnd_family_code[0], perv_cover_code)
                        area = 0
                        self.soil_slope_cover_area_lookup[key] = area

    def code_to_soil_slope_area_subbasin_impervious(self, o_code, area):
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

            hspf_soil_id = int(self.hspf.soil[soil_code][0] + self.hspf.perlnd_family[int(perlnd_group_code)][0]) #TODO should look at separating these
            hspf_slope_id = self.hspf.slope[slope_code][0]
            hspf_perv_cover_id = self.hspf.perv_cover[perv_cover_code][0]
            hspf_implnd_group_id = int(self.hspf.perlnd_family[int(perlnd_group_code)][0])
            hspf_land_use_id = land_use_code

            try:
                self.soil_slope_cover_area_lookup[(hspf_soil_id, hspf_slope_id, hspf_implnd_group_id, hspf_perv_cover_id)] += area
            except:
                print("Not found " + str(hspf_soil_id) + " " + str(hspf_slope_id) + " " + str(hspf_implnd_group_id) +
                      " " + str(hspf_perv_cover_id))

    def future_subbasin_area_to_perlnd_implnd(self, area, area_factor, imp_connectivity=1, include_impervious=True):
        for hspf_soil_id in self.hspf.hspf_soil.keys():
            for hspf_slope_id in self.hspf.hspf_slope.keys():
                for hspf_perv_cover_id in self.hspf.hspf_perv_cover.keys():
                    for perlnd_family_code in self.hspf.perlnd_family.values():
                        try:
                            hspf_imp_cover_id = self.hspf.hspf_imp_cover_id[self.area_type]
                            soil_slope_area = self.soil_slope_cover_area_lookup[(hspf_soil_id, hspf_slope_id, perlnd_family_code[0], hspf_perv_cover_id)]
                            soil_slope_area_factor = soil_slope_area / area
                            if soil_slope_area > 0:
                                self.impervious_area_to_perlnd_implnd(area_factor*soil_slope_area_factor*area,
                                                                      hspf_slope_id,
                                                                      hspf_soil_id,
                                                                      hspf_imp_cover_id,
                                                                      perlnd_family_code[0],
                                                                      imp_connectivity,
                                                                      include_impervious)
                                self.pervious_area_to_perlnd((1-area_factor)*soil_slope_area_factor*area,
                                                             hspf_perv_cover_id,
                                                             hspf_slope_id,
                                                             hspf_soil_id
                                                             )
                                self.area_check_imp += area_factor*soil_slope_area_factor*area
                                self.area_check_perv += (1-area_factor)*soil_slope_area_factor*area
                        except:
                            pass