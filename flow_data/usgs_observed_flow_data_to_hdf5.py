from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData

begin = '2001-10-01'
# end = '2009-12-01'
end = '2022-01-14'
minimum_depth = 0
maximum_depth = 1000
minimum_velocity = 0
maximum_velocity = 10000

location_id = 14211315
temp_monitor1 = TemporaryFlowMonitorData(location_id, True, False, False, minimum_depth=minimum_depth)
temp_monitor1.get_usgs_data(begin, end)
temp_monitor1.filter_usgs_raw_data(5)
output_hdf5 = r"C:\Temp\HSPFWorkshopMaterials\HSPFData\ObservedFlow"
temp_monitor1.flow_data.dropna().to_hdf(output_hdf5 + "\\" + "raw" + str(location_id) + ".h5", mode='w',
                                                key='df')
temp_monitor1.filtered_flow_data.dropna().to_hdf(output_hdf5 + "\\" + "filtered" + str(location_id) + ".h5",
                                                         mode='w', key='df')

try:
    temp_monitor1.flow_data.dropna().to_excel(output_hdf5 + "\\" + "raw" + str(location_id) + ".xlsx")
except:
    print("raw data too large for excel")
try:
    temp_monitor1.filtered_flow_data.dropna().to_excel(
        output_hdf5 + "\\" + "filtered" + str(location_id) + ".xlsx")
except:
    print("filtered data too large for excel")



