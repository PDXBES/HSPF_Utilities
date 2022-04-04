import pandas as pd
import pyodbc
from wdmtoolbox import wdmtoolbox


class EvaporationStation(object):
    def __init__(self):
        self.evap = None
        pass

    def read_evaporation(self, wdm, dsn):
        self.evap = wdmtoolbox.extract(wdm, dsn)
        pass

    def write_evaporation(self, wdm, dsn):
        tstype = 'EVAP'
        base_year = 1948
        tcode = 4
        tstep = 1
        statid = "WILL"
        scenario = "OBSERVED"
        location = "WILL"
        description = "WILL"
        constituent = 'EVAP'
        tsfill = 0.0
        wdmtoolbox.createnewdsn(wdm, dsn, tstype, base_year, tcode, tstep, statid, scenario, location, description, constituent, tsfill)
        wdmtoolbox._writetodsn(wdm, dsn, self.evap)
        pass

    def copy_evaporation(self, wdm, dsn, out_wdm, out_dsn):
        wdmtoolbox.copydsn(wdm, dsn, out_wdm, out_dsn, True)
        pass

    def read_evap_from_csv(self, evap_csv):
        self.evap = pd.read_csv(evap_csv, index_col="Date", usecols=["Date", "Evap"],  header=0, parse_dates=True)
        pass

