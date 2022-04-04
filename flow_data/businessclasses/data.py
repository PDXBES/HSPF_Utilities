import numpy as np
from common.conversion_constants import ConversionConstants
import pandas as pd
from typing import Optional
import math


class Data(object):
    def __init__(self):
        self.conversion_constants = ConversionConstants()

        self.flow_data: Optional[pd.DataFrame] = None
        self.velocity_data: Optional[pd.DataFrame] = None
        self.depth_data: Optional[pd.DataFrame] = None
        self.time_step: Optional[int] = None

        self.filtered_flow_data: Optional[pd.DataFrame] = None
        self.filtered_velocity_data: Optional[pd.DataFrame] = None
        self.filtered_depth_data: Optional[pd.DataFrame] = None
        self.filtered_time_step: Optional[int] = None

#TODO have trouble setting these to nans with downstream plots
#TODO need to check that beg and end dates are within the range of data
    def peak_flow(self, beg, end):
        beg = beg.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        peak_flow = np.float32(self.flow_data.loc[beg:end].max()[0])
        if math.isnan(peak_flow):
            peak_flow = 0
        return peak_flow

    def peak_filtered_flow(self, beg, end):
        beg = beg.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        peak_filtered_flow = np.float32(self.filtered_flow_data.loc[beg:end].max()[0])
        if math.isnan(peak_filtered_flow):
            peak_filtered_flow = 0
        return peak_filtered_flow

    def peak_depth(self, beg, end):
        return np.float32(self.depth_data.loc[beg:end].max()[0])

    def peak_filtered_depth(self, beg, end):
        return np.float32(self.filtered_depth_data.loc[beg:end].max()[0])

    def volume(self, beg, end):
        volume = np.float32(self.flow_data.loc[beg:end].sum()[0]) * \
                 self.time_step * self.conversion_constants.seconds_in_minute / self.conversion_constants.sqft_per_acre
        return volume

    def filtered_volume(self, beg, end):
        volume = np.float32(self.filtered_flow_data.loc[beg:end].sum()[0]) * \
                 self.filtered_time_step * self.conversion_constants.seconds_in_minute / self.conversion_constants.sqft_per_acre
        return volume

    def peak_filtered_flow_as_string(self, beg, end, decimal):
        peak_flow_string = "{:.{}f}".format(self.peak_filtered_flow(beg, end), decimal) + " cfs"
        return peak_flow_string

    def peak_flow_as_string(self, beg, end, decimal):
        peak_flow_string = "{:.{}f}".format(self.peak_flow(beg, end), decimal) + " cfs"
        return peak_flow_string

    def peak_filtered_velocity(self, beg, end):
        return np.float32(self.filtered_velocity_data.loc[beg:end].max()[0])

    def filtered_volume_as_string(self, beg, end, decimal):
        volume_string = "{:.{}f}".format(self.filtered_volume(beg, end), decimal) + " acft"
        return volume_string

    def volume_as_string(self, beg, end, decimal):
        volume_string = "{:.{}f}".format(self.volume(beg, end), decimal) + " acft"
        return volume_string

    def avg_flow_in_cfs_per_water_year(self, flow_data_frame: pd.DataFrame):
        return self.avg_data_frame_per_water_year(flow_data_frame)

    def avg_flow_in_cfs_per_month(self, flow_data_frame: pd.DataFrame):
        return self.avg_data_frame_per_month(flow_data_frame)

    def avg_flow_in_cfs_per_day(self, flow_data_frame: pd.DataFrame):
        return self.avg_flow_in_cfs_per_day(flow_data_frame)

    def filter_data_based_on_data_from_another_source(self, input_data_frame: pd.DataFrame,
                                                      filter_data_frame: pd.DataFrame):
        filtered_data_frame = input_data_frame[input_data_frame.index.isin(filter_data_frame.index)]
        return filtered_data_frame

    def create_filter_mask(self, input_data_frame: pd.DataFrame, filter_data_frame: pd.DataFrame):
        mask = input_data_frame.index.isin(filter_data_frame.index)
        return mask

    def filter_data_for_plotting(self):
        self.flow_data.index.isin(self.filtered_flow_data)

    def compare_avg_data_per_water_year(self, input_data_frame: pd.DataFrame, filter_data_frame: pd.DataFrame):
        filtered_input_data = self.filter_data_based_on_data_from_another_source(input_data_frame, filter_data_frame)
        filtered_input_data_avg_per_water_yr = self.avg_data_frame_per_water_year(filtered_input_data)
        filter_data_avg_per_water_yr = self.avg_data_frame_per_water_year(filter_data_frame)
        avg_data_per_water_year_comparison_data_frame = filtered_input_data_avg_per_water_yr.join(filter_data_avg_per_water_yr)
        if not avg_data_per_water_year_comparison_data_frame.empty:
            avg_data_per_water_year_comparison_data_frame = avg_data_per_water_year_comparison_data_frame.set_index(avg_data_per_water_year_comparison_data_frame.index.to_timestamp().year + 2)
        else:
            avg_data_per_water_year_comparison_data_frame = None
        return avg_data_per_water_year_comparison_data_frame

    def compare_total_volume_data_per_water_year(self, input_data_frame: pd.DataFrame, filter_data_frame: pd.DataFrame):
        filtered_input_data = self.filter_data_based_on_data_from_another_source(input_data_frame, filter_data_frame)
        filtered_input_data_total_per_water_yr = self.total_volume_data_frame_per_water_year(filtered_input_data)
        filter_data_total_per_water_yr = self.total_volume_data_frame_per_water_year(filter_data_frame)
        total_data_per_water_year_comparison_data_frame = filtered_input_data_total_per_water_yr.join(filter_data_total_per_water_yr)
        if not total_data_per_water_year_comparison_data_frame.empty:
            total_data_per_water_year_comparison_data_frame = total_data_per_water_year_comparison_data_frame.set_index(total_data_per_water_year_comparison_data_frame.index.to_timestamp().year + 2)
        else:
            total_data_per_water_year_comparison_data_frame = None
        return total_data_per_water_year_comparison_data_frame

    def compare_avg_data_per_month(self, input_data_frame: pd.DataFrame, filter_data_frame: pd.DataFrame):
        filtered_input_data = self.filter_data_based_on_data_from_another_source(input_data_frame, filter_data_frame)
        filtered_input_data_avg_per_month = self.avg_data_frame_per_month(filtered_input_data)
        filter_data_avg_per_month = self.avg_data_frame_per_month(filter_data_frame)
        avg_data_per_month_comparison_data_frame = filtered_input_data_avg_per_month.join(filter_data_avg_per_month)
        return avg_data_per_month_comparison_data_frame

    def compare_total_volume_data_per_month(self, input_data_frame: pd.DataFrame, filter_data_frame: pd.DataFrame):
        filtered_input_data = self.filter_data_based_on_data_from_another_source(input_data_frame, filter_data_frame)
        filtered_input_data_total_per_month = self.total_volume_data_frame_per_month(filtered_input_data)
        filter_data_total_per_month = self.total_volume_data_frame_per_month(filter_data_frame)
        total_data_per_month_comparison_data_frame = filtered_input_data_total_per_month.join(filter_data_total_per_month)
        return total_data_per_month_comparison_data_frame

    def compare_avg_data_per_day(self, input_data_frame: pd.DataFrame, filter_data_frame: pd.DataFrame):
        filtered_input_data = self.filter_data_based_on_data_from_another_source(input_data_frame, filter_data_frame)
        filtered_input_data_avg_per_day = self.avg_data_frame_per_day(filtered_input_data)
        filter_data_avg_per_day = self.avg_data_frame_per_day(filter_data_frame)
        avg_data_per_day_comparison_data_frame = filtered_input_data_avg_per_day.join(filter_data_avg_per_day)
        return avg_data_per_day_comparison_data_frame

    def avg_data_frame_per_water_year(self, df1: pd.DataFrame):
        df = df1.copy()
        df['Dates'] = df.copy().index.values
        df['WY'] = df.Dates.dt.to_period('A-Sep')
        df['WY'] = df['WY'] - 1
        wy_avg_data_frame = df.groupby('WY').mean()
        return wy_avg_data_frame

    def total_volume_data_frame_per_water_year(self, df1: pd.DataFrame):
        df = df1.copy()
        df['Dates'] = df.copy().index.values
        df['WY'] = df.Dates.dt.to_period('A-Sep')
        df['WY'] = df['WY'] - 1
        wy_total_data_frame = df.groupby('WY').sum()*self.filtered_time_step * self.conversion_constants.seconds_in_minute / self.conversion_constants.sqft_per_acre
        return wy_total_data_frame

    def avg_data_frame_per_month(self, data_frame: pd.DataFrame):
        monthly_avg_data_frame = data_frame.resample('M').mean()
        return monthly_avg_data_frame

    def total_volume_data_frame_per_month(self, data_frame: pd.DataFrame):
        monthly_total_data_frame = data_frame.resample('M').sum() * self.filtered_time_step * self.conversion_constants.seconds_in_minute / self.conversion_constants.sqft_per_acre
        return monthly_total_data_frame

    def avg_data_frame_per_day(self, data_frame: pd.DataFrame):
        daily_avg_data_frame = data_frame.resample('D').mean()
        return daily_avg_data_frame

    def total_volume_data_frame_per_day(self, data_frame: pd.DataFrame):
        daily_total_data_frame = data_frame.resample('D').sum()*self.filtered_time_step * self.conversion_constants.seconds_in_minute / self.conversion_constants.sqft_per_acre
        return daily_total_data_frame


