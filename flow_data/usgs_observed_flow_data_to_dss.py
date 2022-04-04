from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from datetime import datetime
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer, UNDEFINED
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from flow_data.dataio.base_data_io import BaseDataIo


begin_dates = [datetime(year=2001, month=8, day=3, hour=0, minute=0)]
end_dates = [datetime(year=2021, month=11, day=28, hour=0, minute=0)]
basin_names = ["Tryon"]
location_id = [14211315]

input_data = zip(begin_dates, end_dates, basin_names, location_id)

dss_file_path = r"C:\Temp\Tryon.dss"

minimum_depth = 0

# begin = '2001-08-03'
# end = '2021-11-28'

data_io = BaseDataIo()
for begin_date, end_date, basin_name, location_id in input_data:
    usgs_begin_date = begin_date.strftime("%Y-%m-%d")
    usgs_end_date = end_date.strftime("%Y-%m-%d")
    usgs_gage = TemporaryFlowMonitorData(location_id, True, False, True, minimum_depth=minimum_depth)
    usgs_gage.get_usgs_data(usgs_begin_date, usgs_end_date)
    usgs_gage.filter_usgs_raw_data(5)
    regular_flow_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/FLOW//5MIN/5MinInterpolation/"
    irregular_flow_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/FLOW//IR-DECADE/RAW/"
    regular_stage_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/STAGE//5MIN/5MinInterpolation/"
    irregular_stage_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/STAGE//IR-DECADE/RAW/"

    data_io.write_5_minute_filtered_flow_to_regular_dss(dss_file_path, regular_flow_path_name, usgs_gage.filtered_flow_data)
    data_io.write_5_minute_filtered_depth_in_feet_dss(dss_file_path, regular_stage_path_name, usgs_gage.filtered_depth_data)
    data_io.write_raw_flow_data_to_irregular_dss(dss_file_path, irregular_flow_path_name, usgs_gage.flow_data)
    data_io.write_raw_depth_data_in_feet_to_irregular_dss(dss_file_path, irregular_stage_path_name, usgs_gage.depth_data)
