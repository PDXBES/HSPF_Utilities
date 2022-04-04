import pandas as pd
import pyodbc
from wdmtoolbox import wdmtoolbox
import numpy as np

class PrecipitationGage(object):
    def __init__(self, h2_number):
        self.h2_number = h2_number
        self.long_term_avg = None
        self.alternative_gages = []
        self.raw_data = None
        self.filled_data = None

    def fill_precipitation_data(self):
        self.filled_data = self.raw_data.copy()
        for alternative_gage in self.alternative_gages:
            scaling_factor = self.long_term_avg/alternative_gage.long_term_avg
            data_for_filling = alternative_gage.raw_data.copy()
            data_for_filling.loc[:, 'rainfall_amount_inches'] *= scaling_factor
            self.filled_data['rainfall_amount_inches'].fillna(data_for_filling['rainfall_amount_inches'], inplace=True)
            pass

    def get_raw_precipitation_data(self, start_date, end_date, interval, daypart):
        DB = {'servername': 'BESDBPROD1',
              'database': 'NEPTUNE'}

        sql = "EXEC USP_MODEL_RAIN " +\
            " @start_date = " + "'" + start_date + "'" + "," +\
            " @end_date = " + "'" + end_date + "'" + "," +\
            " @interval = " + str(interval) + "," +\
            " @daypart = " + daypart + "," +\
            " @h2_number = " + str(self.h2_number) + "," + \
            " @adjust_for_dst = false" + "," + \
            " @limit_rows = -1"

        # create the connection
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DB['servername'] + ';DATABASE=' + DB['database'] + ';Trusted_Connection=yes')
        with conn:
            self.raw_data = pd.read_sql(sql, conn, index_col="date_time")
            #self.raw_data = self.raw_data[self.raw_data['sensor_present'] == 'Y']
            #self.raw_data = self.raw_data[self.raw_data['downtime'] == 'N']
            #self.raw_data = self.raw_data.dropna(subset=['rainfall_amount_inches'])
            self.raw_data.drop(['sensor_present', 'downtime', 'h2_number', 'time_zone'], axis=1, inplace=True)
            pass

    def write_raw_data_to_wdm(self, wdm, tcode, tstep):
        tstype = 'PREC'
        base_year = 1948
        # tcode -> 2 minute 3 hour
        # tstep = 1
        statid = str(self.h2_number)
        scenario = "OBSERVED"
        location = str(self.h2_number)
        description = str(self.h2_number)
        constituent = 'PREC'
        tsfill = -999.0
        dsn = self.h2_number + 1000
        wdmtoolbox.createnewdsn(wdm, dsn, tstype, base_year, tcode, tstep, statid, scenario, location, description, constituent, tsfill)
        #self.raw_data = self.raw_data.tshift()
        wdmtoolbox._writetodsn(wdm, dsn, self.raw_data)

    def write_filled_data_to_wdm(self, wdm, tcode, tstep):
        tstype = 'PREC'
        base_year = 1948
        # tcode -> 2 minute 3 hour
        # tstep = 1
        statid = str(self.h2_number)
        scenario = "OBSERVED"
        location = str(self.h2_number)
        description = str(self.h2_number)
        constituent = 'PREC'
        tsfill = 0.0  #TODO need to provide feedback on fill
        dsn = self.h2_number
        wdmtoolbox.createnewdsn(wdm, dsn, tstype, base_year, tcode, tstep, statid, scenario, location, description, constituent, tsfill)
#        self.filled_data = self.filled_data.tshift()
        wdmtoolbox._writetodsn(wdm, dsn, self.filled_data)

    @staticmethod
    def write_design_storm_to_wdm(wdm, dsn, storm, tcode, tstep, design_storm_data):
        tstype = 'PREC'
        base_year = 1948
        # tcode -> 2 minute 3 hour
        # tstep = 1
        statid = storm
        location = "PDX"
        description = storm + "5 min Design Storm"
        scenario = "OBSERVED"
        constituent = 'PREC'
        tsfill = 0.0  #TODO need to provide feedback on fill
        wdmtoolbox.createnewdsn(wdm, dsn, tstype, base_year, tcode, tstep, statid, scenario, location, description, constituent, tsfill)
        design_storm_data = design_storm_data.shift()  # tshift deprecated
        wdmtoolbox._writetodsn(wdm, dsn,  design_storm_data)

    def read_filled_data_from_wdm(self, wdm, start_date=None, end_date=None):
        self.filled_data = wdmtoolbox.extract(wdm, self.h2_number).fillna(0)
        if start_date is not None and end_date is not None:
            self.filled_data = self.filled_data.loc[start_date:end_date]
        pass

    def read_raw_data_from_wdm(self, wdm, start_date=None, end_date=None):
        self.raw_data = wdmtoolbox.extract(wdm, self.h2_number + 1000)
        if start_date is not None and end_date is not None:
            self.raw_data = self.raw_data.loc[start_date:end_date]
        pass

    def peak_precipitation(self, beg, end):
        beg = beg.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        return np.float32(self.filled_data.loc[beg:end].max()[0])

    def total_precipitation(self, beg, end):
        beg = beg.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        total_precipitation = np.float32(self.filled_data.loc[beg:end].sum()[0])
        return total_precipitation
