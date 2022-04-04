class Implnd(object):
    """Impervious Land Surface"""
    def __init__(self, hspf, imp_cover, slope, implnd_id):
        self.area = 0
        self.hspf_cover_id = hspf.hspf_imp_cover_id[imp_cover]
        self.hspf_slope_id = hspf.hspf_slope_id[slope]
        self.implnd_id = implnd_id
        self.desc = imp_cover + "/" + slope