class Perlnd(object):
    """Pervious Land Surface"""
    def __init__(self, hspf, perv_cover, slope, soil, perlnd_id):
        self.area = 0
        self.hspf_cover_id = hspf.hspf_perv_cover_id[perv_cover]
        self.hspf_slope_id = hspf.hspf_slope_id[slope]
        self.hspf_soil_id = hspf.hspf_soil_id[soil]
        self.perlnd_id = perlnd_id
        self.desc = hspf.hspf_perv_cover[self.hspf_cover_id] + ", " + \
                    hspf.hspf_slope[self.hspf_slope_id] + ", " + \
                    hspf.hspf_soil[self.hspf_soil_id]
