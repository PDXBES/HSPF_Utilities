import pandas as pd
import pyodbc
try:
    from wdmtoolbox import wdmtoolbox
except:
    print("WDMToolbox not imported")
import csv
from flow_data.businessclasses.data import Data
try:
    import dataretrieval.nwis as nwis
except:
    print("dataretrieval not imported")
from datetime import datetime


class ObservedData(Data):
    def __init__(self, location_id, node_name="1", flow=None, velocity=None, depth=None, minimum_depth=0.8, maximum_depth=10000, minimum_velocity=-100, maximum_velocity=100):
        super().__init__()
        self.location_id = location_id
        self.drainage_area = None
        self.node_name = node_name
        self.link_name = None
        self.raw_data = None
        self.flow = flow
        self.velocity = velocity
        self.depth = depth
        self.minimum_depth = minimum_depth
        self.maximum_depth = maximum_depth
        self.minimum_velocity = minimum_velocity
        self.maximum_velocity = maximum_velocity
        self.location_data = None
        self.visit_data = None
        self.filtered_data = None

    def get_filtered_flow_data_from_hdf5(self, file_path):
        self.filtered_flow_data = pd.DataFrame(pd.read_hdf(file_path))

    def get_flow_data_from_hdf5(self, file_path):
        self.flow_data = pd.DataFrame(pd.read_hdf(file_path))

    def get_usgs_data(self, start_date, end_date, diameter_in_ft):
        self.raw_data = nwis.get_record(sites=str(self.location_id), service='iv', start=start_date, end=end_date)
        self.process_raw_usgs_data()

    def get_raw_data(self, start_date, end_date):
        DB = {'servername': 'BESDBPROD1',
              'database': 'JANUS'}

        sql = "Exec USP_GET_READINGS_FROM_LOCATION " + \
            "@loc_id = " + str(self.location_id) + "," + \
            "@start_date = '" + start_date + "'," + \
            "@end_date = '" + end_date + "'"

        # create the connection
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DB['servername'] + ';DATABASE=' + DB[
            'database'] + ';Trusted_Connection=yes')
        with conn:
            self.raw_data = pd.read_sql(sql, conn, index_col="reading_datetime")
            self.process_raw_data()

    def get_raw_data_hydra_data(self, start_date, end_date, diameter_in_ft):
        DB = {'servername': 'BESDBPROD1',
              'database': 'NEPTUNE'}

        sql = "declare @h2_num as int = " + str(self.location_id) + "\n" \
              "declare @Vlocqual as varchar(20) = 'downstream'\n" \
              "declare @Dlocqual as varchar(20) = 'downstream'\n" \
              "declare @DiaFt as float = " + str(diameter_in_ft) + "\n" \
              "declare @sdate as date = " + "'" + start_date + "'" + "\n" \
              "declare @edate as date = " + "'" + end_date + "'" + "\n" \
              "Select @h2_num as location_id, @Dlocqual as DLocQual, JoinData3.D05 as DateTime, JoinData3.Avgdepth as depth_inches, '+' as depth_qual, JoinData3.AVGvel as velocity_fps, '+' as velocity_qual, JoinData3.areaft*JoinData3.AVGvel as FlowCFS from \n" \
              "(Select JoinData2.D05, JoinData2.Avgdepth, JoinData2.AVGvel, JoinData2.x, JoinData2.alpha,  0.5 * power(@DiaFt/2, 2) * (alpha - Sin(alpha)) as areaft from \n" \
              "(Select JoinData.D05, JoinData.Avgdepth, JoinData.AVGvel, x, 2* (atan(-joindata.x/power(-(joindata.x) * joindata.x + 1,0.5))+2*atan(1)) as alpha from \n" \
              "(Select Ddata.D05, Ddata.Avgdepth, Vdata.AVGvel, (SELECT CASE WHEN AVGDepth/12  > @DiaFt THEN (1 - 2 * .99999*@DiaFt / @DiaFt) ELSE (SELECT CASE WHEN AVGDepth = 0 THEN (1 - 2 * 0.25/12 / @DiaFt) ELSE (1 - 2 * AVgdepth/12 / @DiaFt) END) END)  as x    from \n" \
              "(select DATETIMEFROMPARTS(DATEPART(YEAR, dbo.DEPTH_DATA.assigned_sample_time), DATEPART(MONTH, dbo.DEPTH_DATA.assigned_sample_time),DATEPART(DAY, dbo.DEPTH_DATA.assigned_sample_time), DATEPART(HOUR, dbo.DEPTH_DATA.assigned_sample_time), (DATEPART(MINUTE, dbo.DEPTH_DATA.assigned_sample_time) / 5)*5 ,0,0) as D05, AVG(dbo.depth_data.final_value) as AVGDepth\n" \
              "From [dbo].[DEPTH_DATA] inner join [dbo].[STATION] on station.station_id = DEPTH_DATA.station_id\n" \
              "WHERE ((dbo.station.h2_number=@h2_num) AND (dbo.DEPTH_DATA.location_qualifier=@Dlocqual) AND ((dbo.DEPTH_DATA.assigned_sample_time) Between @sdate And @edate))" \
              "group by DATETIMEFROMPARTS(DATEPART(YEAR, dbo.DEPTH_DATA.assigned_sample_time), DATEPART(MONTH, dbo.DEPTH_DATA.assigned_sample_time),DATEPART(DAY, dbo.DEPTH_DATA.assigned_sample_time), DATEPART(HOUR, dbo.DEPTH_DATA.assigned_sample_time), (DATEPART(MINUTE, dbo.DEPTH_DATA.assigned_sample_time) / 5)*5,0,0)) as Ddata\n" \
              "inner join" \
              "(select DATETIMEFROMPARTS(DATEPART(YEAR, dbo.VELOCITY_DATA.assigned_sample_time), DATEPART(MONTH, dbo.VELOCITY_DATA.assigned_sample_time),DATEPART(DAY, dbo.VELOCITY_DATA.assigned_sample_time), DATEPART(HOUR, dbo.VELOCITY_DATA.assigned_sample_time), (DATEPART(MINUTE, dbo.VELOCITY_DATA.assigned_sample_time) / 5)*5 ,0,0) as D05, AVG(dbo.VELOCITY_DATA.final_value) as AVGVel\n" \
              "From [dbo].[velocity_DATA] inner join [dbo].[STATION] on station.station_id = VELOCITY_DATA.station_id\n" \
              "WHERE ((dbo.station.h2_number=@h2_num) AND (dbo.VELOCITY_DATA.location_qualifier=@Vlocqual) AND ((dbo.VELOCITY_DATA.assigned_sample_time) Between @sdate And @edate))\n" \
              "group by DATETIMEFROMPARTS(DATEPART(YEAR, dbo.VELOCITY_DATA.assigned_sample_time), DATEPART(MONTH, dbo.VELOCITY_DATA.assigned_sample_time),DATEPART(DAY, dbo.VELOCITY_DATA.assigned_sample_time), DATEPART(HOUR, dbo.VELOCITY_DATA.assigned_sample_time), (DATEPART(MINUTE, dbo.VELOCITY_DATA.assigned_sample_time) / 5)*5,0,0)) as Vdata\n" \
              "on Ddata.D05 = vdata.D05) as JoinData" \
              ") as JoinData2\n" \
              ") as JoinData3\n" \
              "order by D05"

        # create the connection
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DB['servername'] + ';DATABASE=' + DB[
            'database'] + ';Trusted_Connection=yes')
        with conn:
            self.raw_data = pd.read_sql(sql, conn, index_col="DateTime")
            self.process_raw_hydra_data()

    def get_raw_data_from_excel(self, excel_file_path):
        self.raw_data = pd.read_excel(excel_file_path, index_col=0)
        self.process_raw_data()

    def get_aquarius_depth_data(self, url):
        self.depth_data = pd.read_csv(url)
        "https://aquarius.portlandoregon.gov/Export/DataSet?DataSet=Water%20Level.Primary%40TC-19&ExportFormat=csv&Compressed=true&RoundData=False&Unit=82&Timezone=-8&_=1634316851875"

    def process_raw_usgs_data(self):
        self.node_name = str(self.location_id)
        # if self.flow and self.depth:
        #     self.raw_data = self.raw_data.dropna()
        #     self.flow_data = self.raw_data['00060'].to_frame()
        #     self.flow_data['date'] = pd.to_datetime(self.flow_data.index, utc=True)
        #     self.flow_data['date'] = self.flow_data['date'].dt.tz_convert(tz='US/Pacific')
        #     self.flow_data['date'] = self.flow_data['date'].dt.tz_localize(tz=None)
        #     self.flow_data = self.flow_data.set_index('date')
        #
        #     self.depth_data = self.raw_data['00065'].to_frame()
        #     self.depth_data['date'] = pd.to_datetime(self.depth_data.index, utc=True)
        #     self.depth_data['date'] = self.depth_data['date'].dt.tz_convert(tz='US/Pacific')
        #     self.depth_data['date'] = self.depth_data['date'].dt.tz_localize(tz=None)
        #     self.depth_data = self.depth_data.set_index('date')
        #
        # else:
        if self.flow:
            self.flow_data = self.raw_data['00060'].to_frame()
            self.flow_data['date'] = pd.to_datetime(self.flow_data.index, utc=True)
            self.flow_data['date'] = self.flow_data['date'].dt.tz_convert(tz='Etc/GMT+8')
            #self.flow_data['date'] = self.flow_data['date'].dt.tz_convert(tz='US/Pacific')
            self.flow_data['date'] = self.flow_data['date'].dt.tz_localize(tz=None)
            self.flow_data = self.flow_data.set_index('date')
        if self.depth:
            try:
                self.depth_data = self.raw_data['00065'].to_frame()
            except:
                self.depth_data = self.raw_data.iloc[:, 3].to_frame()
            self.depth_data['date'] = pd.to_datetime(self.depth_data.index, utc=True)
            self.depth_data['date'] = self.depth_data['date'].dt.tz_convert(tz='Etc/GMT+8')
            self.depth_data['date'] = self.depth_data['date'].dt.tz_localize(tz=None)
            self.depth_data = self.depth_data.set_index('date')

    def process_raw_data(self):
        if self.flow:
            self.flow_data = self.raw_data.drop(['location_id', 'project_id',
                                                 'depth_inches', 'depth_qual',
                                                 'velocity_fps', 'velocity_qual'], axis=1)
            flow_column = self.flow_data.columns[0]

        if self.velocity:
            self.velocity_data = self.raw_data.drop(['location_id', 'project_id',
                                                     'depth_inches', 'depth_qual',
                                                     'velocity_qual', flow_column], axis=1)
        if self.depth:
            self.depth_data = self.raw_data.drop(['location_id', 'project_id',
                                                      'depth_qual',
                                                      'velocity_fps', 'velocity_qual', flow_column], axis=1)
        pass

    def process_raw_hydra_data(self):
        if self.flow:
            self.flow_data = pd.DataFrame(self.raw_data["FlowCFS"])
            flow_column = "FlowCFS"

        if self.velocity:
            self.velocity_data = pd.DataFrame(self.raw_data["velocity_fps"])
        if self.depth:
            self.depth_data = pd.DataFrame(self.raw_data["depth_inches"])
        pass

    def swap_velocity_and_flow(self, begin_date, end_date):
        swap_velocity = self.flow_data.loc[begin_date: end_date].copy(deep=True)
        swap_flow = self.velocity_data.loc[begin_date: end_date].copy(deep=True)
        self.flow_data.loc[begin_date: end_date] = swap_flow
        self.velocity_data.loc[begin_date: end_date] = swap_velocity

    def swap_velocity_and_depth(self, begin_date, end_date):
        swap_velocity = self.depth_data.loc[begin_date: end_date].copy(deep=True)
        swap_depth = self.velocity_data.loc[begin_date: end_date].copy(deep=True)
        self.depth_data.loc[begin_date: end_date] = swap_depth
        self.velocity_data.loc[begin_date: end_date] = swap_velocity

    def get_location_data(self):
        DB = {'servername': 'BESDBPROD1',
              'database': 'JANUS'}

        sql = "Exec dbo.USP_GET_PROJECT_INFO_FROM_LOCATION " + \
            "@loc_id = " + str(self.location_id)

        # create the connection
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DB['servername'] + ';DATABASE=' + DB[
            'database'] + ';Trusted_Connection=yes')
        with conn:
            self.location_data = pd.read_sql(sql, conn)

    def get_visit_data(self, start_date, end_date):
        DB = {'servername': 'BESDBPROD1',
              'database': 'JANUS'}

        sql = "EXEC dbo.USP_GET_NOTES_FROM_LOCATION " + \
            "@loc_id = " + str(self.location_id)

        # create the connection
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DB['servername'] + ';DATABASE=' + DB[
            'database'] + ';Trusted_Connection=yes')
        with conn:
            self.visit_data = pd.read_sql(sql, conn)
            self.visit_data['visit_date'] = pd.to_datetime(self.visit_data['visit_date'])
            self.visit_data.set_index('visit_date', inplace=True)
            self.visit_data = self.visit_data.loc[start_date:end_date]

    def upload_dates(self):
        return self.visit_data[self.visit_data['meter_visit_type'] == 'Upload'].index.values

    def number_of_upload_dates(self):

        return self.visit_data[self.visit_data['meter_visit_type'] == 'Upload'].index.values.size

    def installation_dates(self):
        return self.visit_data[self.visit_data['meter_visit_type'] == 'Installation'].index.values

    def removal_dates(self):
        return self.visit_data[self.visit_data['meter_visit_type'] == 'Removal'].index.values

    def repair_dates(self):
        return self.visit_data[self.visit_data['meter_visit_type'] == 'Repair'].index.values

    def check_dates(self):
        return self.visit_data[self.visit_data['meter_visit_type'] == 'Check'].index.values

    def sensor_replacement_dates(self):
        return self.visit_data[self.visit_data['meter_visit_type'] == 'Sensor Replacement'].index.values

    # def write_raw_data_to_wdm(self, wdm):
    #     tstype = 'FLOW'
    #     base_year = 1948
    #     tcode = 2
    #     tstep = 5
    #     statid = str(self.node_name)
    #     scenario = "OBSERVED"
    #     location = str(self.node_name)
    #     description = str(self.node_name)
    #     constituent = 'FLOW'
    #     tsfill = -999.0
    #     self.flow_data.tshift()
    #     wdmtoolbox.createnewdsn(wdm, self.location_id, tstype, base_year, tcode, tstep, statid, scenario, location, description, constituent, tsfill)
    #     wdmtoolbox._writetodsn(wdm, self.location_id, self.flow_data)

    def filter_usgs_raw_data(self, avg_timestep_in_minutes):
        self.filtered_time_step = avg_timestep_in_minutes
        if self.flow and self.depth:
            self.filtered_flow_data = self.flow_data
            self.filtered_depth_data = self.depth_data
        elif self.flow:
            self.filtered_flow_data = self.flow_data
        elif self.depth:
            self.filtered_depth_data = self.depth_data

        resample_interval = str(self.filtered_time_step) + 'min'
        if self.flow:
            self.filtered_flow_data = self.filtered_flow_data[~self.filtered_flow_data.index.duplicated(keep='first')]
            #self.filtered_flow_data = self.filtered_flow_data.resample(resample_interval).interpolate(limit=6, limit_area = 'inside') # pad will just repeat rather than interpolate
            self.filtered_flow_data = self.filtered_flow_data.resample(resample_interval).asfreq()
            data_column = self.filtered_flow_data.columns[0]
            self.filtered_flow_data['NoIterp'] = self.filtered_flow_data[data_column]
            i = self.filtered_flow_data[data_column].isna()
            m = (self.filtered_flow_data.groupby(i.ne(i.shift()).cumsum().values)[data_column].transform('size').le(5) & i)
            m = m[m==True]
            self.filtered_flow_data[data_column] = self.filtered_flow_data[data_column].interpolate()
            self.filtered_flow_data = self.filtered_flow_data[self.filtered_flow_data.index.isin(m.index) | ~self.filtered_flow_data['NoIterp'].isna()]
            self.filtered_flow_data = pd.DataFrame(self.filtered_flow_data[data_column].resample(resample_interval).asfreq())

        if self.depth:
            self.filtered_depth_data = self.filtered_depth_data[~self.filtered_depth_data.index.duplicated(keep='first')]
            self.filtered_depth_data = self.filtered_depth_data.resample(resample_interval).asfreq()
            data_column = self.filtered_depth_data.columns[0]
            self.filtered_depth_data['NoIterp'] = self.filtered_depth_data[data_column]
            i = self.filtered_depth_data[data_column].isna()
            m = (self.filtered_depth_data.groupby(i.ne(i.shift()).cumsum().values)[data_column].transform('size').le(5) & i)
            m = m[m == True]
            self.filtered_depth_data[data_column] = self.filtered_depth_data[data_column].interpolate()
            self.filtered_depth_data = self.filtered_depth_data[
                self.filtered_depth_data.index.isin(m.index) | ~self.filtered_depth_data['NoIterp'].isna()]
            self.filtered_depth_data = pd.DataFrame(self.filtered_depth_data[data_column].resample(resample_interval).asfreq())

    def filter_raw_data(self, avg_timestep_in_minutes):
        self.filtered_time_step = avg_timestep_in_minutes
        if self.flow and self.velocity and self.depth:
            self.filtered_data = self.raw_data[((self.raw_data.depth_qual == '+') | (self.raw_data.depth_qual.isna())) &
                                               ((self.raw_data.velocity_qual == '+') | (self.raw_data.velocity_qual.isna()))
                                               & (self.raw_data[self.flow_data.columns[0]] > 0)
                                               & (self.raw_data.depth_inches >= self.minimum_depth)
                                               & (self.raw_data.depth_inches <= self.maximum_depth)
                                               & (self.raw_data.velocity_fps >= self.minimum_velocity)
                                               & (self.raw_data.velocity_fps <= self.maximum_velocity)]
        elif self.flow and self.depth:
            self.filtered_data = self.raw_data[(self.raw_data.depth_qual == '+') & (self.raw_data[self.flow_data.columns[0]] > 0) &
                                               (self.raw_data.depth_inches >= self.minimum_depth) &
                                               (self.raw_data.depth_inches <= self.maximum_depth)]
        elif self.depth:
            self.filtered_data = self.raw_data[(self.raw_data.depth_qual == '+') &
                                               (self.raw_data.depth_inches >= self.minimum_depth) &
                                                (self.raw_data.depth_inches <= self.maximum_depth)]

        if self.flow:
            self.filtered_flow_data = self.filtered_data.drop(['location_id', 'project_id',
                                                'depth_inches', 'depth_qual',
                                                'velocity_fps', 'velocity_qual'], axis=1)
            self.filtered_flow_data = self.filtered_flow_data[self.filtered_flow_data[self.filtered_flow_data.columns[0]] > 0]
        if self.depth:
            self.filtered_depth_data = self.filtered_data.drop(['location_id', 'project_id',
                                                    'depth_qual',
                                                    'velocity_fps', 'velocity_qual',
                                                    self.filtered_flow_data.columns[0]], axis=1)

        if self.velocity:
            self.filtered_velocity_data = self.filtered_data.drop(['location_id', 'project_id',
                                                'depth_qual',
                                                'depth_inches', 'velocity_qual',
                                                self.filtered_flow_data.columns[0]], axis=1)

        resample_interval = str(self.filtered_time_step) + 'min'
        if self.flow:
            self.filtered_flow_data = self.filtered_flow_data.resample(resample_interval).mean()
            self.filtered_flow_data = self.filtered_flow_data.interpolate(limit=2)
        if self.depth:
            self.filtered_depth_data = self.filtered_depth_data.resample(resample_interval).mean()
            self.filtered_depth_data = self.filtered_depth_data.interpolate(limit=2)
        if self.velocity:
            self.filtered_velocity_data = self.filtered_velocity_data.resample(resample_interval).mean()
            self.filtered_velocity_data = self.filtered_velocity_data.interpolate(limit=2)
        pass

    def swap_filtered_velocity_and_flow(self, begin_date, end_date):
        swap_velocity = self.filtered_flow_data.loc[begin_date: end_date].copy(deep=True)
        swap_flow = self.filtered_velocity_data.loc[begin_date: end_date].copy(deep=True)
        self.filtered_flow_data.loc[begin_date: end_date] = swap_flow
        self.filtered_velocity_data.loc[begin_date: end_date] = swap_velocity

    def swap_filtered_velocity_and_depth(self, begin_date, end_date):
        swap_velocity = self.filtered_depth_data.loc[begin_date: end_date].copy(deep=True)
        swap_depth = self.filtered_velocity_data.loc[begin_date: end_date].copy(deep=True)
        self.filtered_depth_data.loc[begin_date: end_date] = swap_depth
        self.filtered_velocity_data.loc[begin_date: end_date] = swap_velocity

    # def _write_timeseries_file_header(self, interface_file):
    #     with open(interface_file, 'w') as interfacefile:
    #         interfacefile.write(";Flow Data for link M76337\n")
    #         interfacefile.write("M76337\n")
    #
    # def write_timeseries_file(self, interface_file):
    #     ### Writes calibration file for SWMM
    #     self._write_timeseries_file_header(interface_file)
    #     flow_df = self.flow_data.reset_index()
    #     flow_df.to_csv(interface_file, mode='a', header=False, sep=' ', float_format="%.5f", index=False,
    #                    date_format="%m/%d/%Y %H:%M", quoting=csv.QUOTE_NONE, escapechar=' ')

