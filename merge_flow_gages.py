import pandas as pd

output_hdf5 = r"v:\hydromodhspf\Models\HSPFWorkshopMaterials\HSPFData\ObservedFlow"

location_ids = [4283, 10372]
raw_data_hdf5s = []
filtered_data_hdf5s = []

location_ids_str = ""
for location_id in location_ids:
    raw_data_path = output_hdf5 + "\\" + "raw" + str(location_id) + ".h5"
    filtered_data_path = output_hdf5 + "\\" + "filtered" + str(location_id) + ".h5"
    raw_data_df = pd.read_hdf(raw_data_path)
    filtered_data_df = pd.read_hdf(filtered_data_path)
    raw_data_hdf5s.append(raw_data_df)
    filtered_data_hdf5s.append(filtered_data_df)
    location_ids_str += str(location_id) + "_"

location_ids_str = location_ids_str[0:-1]

merged_raw_data = pd.concat(raw_data_hdf5s)
merged_filtered_data = pd.concat(filtered_data_hdf5s)

raw_data_output = output_hdf5 + "\\" + "raw" + str(location_ids_str) + ".h5"
merged_raw_data.to_hdf(raw_data_output, mode='w', key='df')

filtered_data_output = output_hdf5 + "\\" + "filtered" + str(location_ids_str) + ".h5"
merged_filtered_data.to_hdf(filtered_data_output, mode='w', key='df')