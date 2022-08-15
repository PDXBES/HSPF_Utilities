from datetime import datetime
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer, UNDEFINED
import numpy as np
import pandas as pd


class BaseDataIo():
    def write_5_minute_filtered_flow_to_regular_dss(self, dss_file_path, path_name, filtered_flow_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "CFS"
        interval_in_minutes = 5
        begin_date = filtered_flow_data.index.values[0].astype('M8[ms]').astype('O')
        start_date = begin_date.strftime("%d") + str.upper(begin_date.strftime("%h")) + begin_date.strftime("%Y") + " " + begin_date.strftime("%H:%M:%S")  # "03AUG2001 00:00:00"
        self.write_data_to_regular_dss(dss_file_path, path_name, start_date, filtered_flow_data, data_type, units,  interval_in_minutes)

    def write_5_minute_precipitation_dss(self, dss_file_path, path_name, precipiation_data: pd.DataFrame):
        data_type = "PER-CUM"
        units = "INCH"
        interval_in_minutes = 5
        begin_date = precipiation_data.index.values[0].astype('M8[ms]').astype('O')
        start_date = begin_date.strftime("%d") + str.upper(begin_date.strftime("%h")) + begin_date.strftime("%Y") + " " + begin_date.strftime("%H:%M:%S")  # "03AUG2001 00:00:00"
        self.write_data_to_regular_dss(dss_file_path, path_name, start_date, precipiation_data, data_type, units,  interval_in_minutes)

    def write_5_minute_filtered_depth_in_feet_dss(self, dss_file_path, path_name, depth_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "FEET"
        interval_in_minutes = 5
        begin_date = depth_data.index.values[0].astype('M8[ms]').astype('O')
        start_date = begin_date.strftime("%d") + str.upper(begin_date.strftime("%h")) + begin_date.strftime("%Y") + " " + begin_date.strftime("%H:%M:%S")  # "03AUG2001 00:00:00"
        self.write_data_to_regular_dss(dss_file_path, path_name, start_date, depth_data, data_type, units,  interval_in_minutes)

    def write_5_minute_filtered_velocity_in_feet_per_second_dss(self, dss_file_path, path_name, velocity_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "FEET/SEC"
        interval_in_minutes = 5
        begin_date = velocity_data.index.values[0].astype('M8[ms]').astype('O')
        start_date = begin_date.strftime("%d") + str.upper(begin_date.strftime("%h")) + begin_date.strftime("%Y") + " " + begin_date.strftime("%H:%M:%S")  # "03AUG2001 00:00:00"
        self.write_data_to_regular_dss(dss_file_path, path_name, start_date, velocity_data, data_type, units,  interval_in_minutes)

    def write_5_minute_filtered_depth_in_inches_dss(self, dss_file_path, path_name, depth_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "INCH"
        interval_in_minutes = 5
        begin_date = depth_data.index.values[0].astype('M8[ms]').astype('O')
        start_date = begin_date.strftime("%d") + str.upper(begin_date.strftime("%h")) + begin_date.strftime("%Y") + " " + begin_date.strftime("%H:%M:%S")  # "03AUG2001 00:00:00"
        self.write_data_to_regular_dss(dss_file_path, path_name, start_date, depth_data, data_type, units,  interval_in_minutes)

    def write_data_to_regular_dss(self, dss_file_path, path_name, start_date, data: pd.DataFrame, data_type, units, interval_in_minutes):
        dsn_missing_data_flag = -901
        resample_interval = str(interval_in_minutes) + 'min'
        data = data.resample(resample_interval).asfreq().fillna(dsn_missing_data_flag)
        tsc = TimeSeriesContainer()
        tsc.pathname = path_name
        tsc.startDateTime = start_date
        tsc.numberValues = len(data.index)
        tsc.units = units
        tsc.type = data_type
        tsc.interval = interval_in_minutes
        tsc.values = list(data.values)

        with HecDss.Open(dss_file_path) as fid:
            fid.deletePathname(tsc.pathname)
            fid.put_ts(tsc)

    def write_raw_flow_data_to_irregular_dss(self, dss_file_path, path_name, flow_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "CFS"
        self.write_data_to_irregular_dss(dss_file_path, path_name, flow_data, data_type, units)

    def write_raw_depth_data_in_feet_to_irregular_dss(self, dss_file_path, path_name, depth_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "FEET"
        self.write_data_to_irregular_dss(dss_file_path, path_name, depth_data, data_type, units)

    def write_raw_depth_data_in_inches_to_irregular_dss(self, dss_file_path, path_name, depth_data: pd.DataFrame):
        data_type = "INST-VAL"
        units = "INCH"
        self.write_data_to_irregular_dss(dss_file_path, path_name, depth_data, data_type, units)

    def write_raw_precipitation_dss(self, dss_file_path, path_name, precipiation_data: pd.DataFrame):
        data_type = "PER-CUM"
        units = "INCH"
        self.write_data_to_irregular_dss(dss_file_path, path_name, precipiation_data, data_type, units)

    def write_data_to_irregular_dss(self, dss_file_path, path_name, data: pd.DataFrame, data_type, units):
        tsc = TimeSeriesContainer()
        tsc.numberValues = len(data.index)
        tsc.pathname = path_name
        tsc.units = units
        tsc.type = data_type
        tsc.interval = -1
        tsc.values = list(data.values[:, 0])
        data.reset_index(inplace=True)
        date_column = data.columns[0]
        tsc.times = list(data[date_column].dt.to_pydatetime())
        with HecDss.Open(dss_file_path) as fid:
            fid.deletePathname(tsc.pathname)
            fid.put_ts(tsc)