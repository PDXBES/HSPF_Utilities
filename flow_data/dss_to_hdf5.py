from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer, UNDEFINED
import pandas as pd
import numpy as np
from pydsstools.heclib.utils import dss_logging
dss_logging.config(level='None')

dss_file_path = r"V:\HydroModHSPF\Models\Tryon\Tryon1996.dss"
output_hdf5 = r"V:\HydroModHSPF\Models\Tryon"

location_id = 19965365
basin_name = "Arnold Creek"
name = "SW Arnold St"

# location_id = 19961156
# basin_name = "Tryon Creek"
# name = "Boones Ferry Road"
regular_flow_path_name_raw = "/" + basin_name + "/" + name + "/Flow//5MIN/obs/"
regular_flow_path_name_filtered = "/" + basin_name + "/" + name + "/Flow//5MIN/obs_filtered/"

fid = HecDss.Open(dss_file_path )
ts = fid.read_ts(regular_flow_path_name_filtered, trim_missing=True)
filtered_flow_df = pd.DataFrame(data = {'flow_cfs_AxV': ts.values}, index=ts.pytimes)
filtered_flow_df.index.name = 'reading_datetime'
filtered_flow_df.to_hdf(output_hdf5 + "\\" + "filtered" + str(location_id) + ".h5", mode='w', key='df')
try:
    filtered_flow_df.to_excel(output_hdf5 + "\\" + "filtered" + str(location_id) + ".xlsx")
except:
    print("filtered data too large for excel")


ts = fid.read_ts(regular_flow_path_name_raw, trim_missing=True)
raw_flow_df = pd.DataFrame(data = {'flow_cfs_AxV': ts.values}, index=ts.pytimes)
raw_flow_df.index.name = 'reading_datetime'
raw_flow_df.to_hdf(output_hdf5 + "\\" + "raw" + str(location_id) + ".h5", mode='w', key='df')
try:
    raw_flow_df.to_excel(output_hdf5 + "\\" + "raw" + str(location_id) + ".xlsx")
except:
    print("raw data too large for excel")