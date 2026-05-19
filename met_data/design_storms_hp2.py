from met_data.businessclasses.precipitation_gage import PrecipitationGage
import pandas as pd
from met_data.businessclasses.evaporation import EvaporationStation
import math

output_hdf5 = r"C:\Temp\Met5minDesignStorms.h5"
design_storm_spreadsheet = r'C:\Users\SGOULD\Documents\HSPF_Utilities\met_data\design_storm_data\DesignStorms.xlsx'
design_storm_test_spreadsheet = r'c:\temp\design_storm_test.xlsx'
evap_csv = r"\\BESFile1\ASM_Projects\HydroModHSPF\Evap\evap.csv"

with pd.ExcelWriter(design_storm_test_spreadsheet) as writer:
    avg_year_storm_shifted_sheet_name = "ShiftedAvgYr5min"
    avg_year_storm_shifted_df = pd.read_excel(design_storm_spreadsheet, sheet_name=avg_year_storm_shifted_sheet_name, usecols=['Date', 'Depth'], index_col="Date", header=0)
    avg_year_storm_shifted_df.index = avg_year_storm_shifted_df.index.round(freq='min')
    avg_year_storm_shifted_df.rename(columns={'Depth': 'rainfall_amount_inches'}, inplace=True)
    avg_year_storm_shifted_df.to_excel(writer, sheet_name=avg_year_storm_shifted_sheet_name)
    precipitation_gage = PrecipitationGage(1)

    avg_year_storm_shifted_sheet_name = "LeapShiftedAvgYr5min"
    avg_year_storm_shifted_leap_year_df = pd.read_excel(design_storm_spreadsheet, sheet_name=avg_year_storm_shifted_sheet_name, usecols=['Date', 'Depth'], index_col="Date", header=0)
    avg_year_storm_shifted_leap_year_df.index = avg_year_storm_shifted_leap_year_df.index.round(freq='min')
    avg_year_storm_shifted_leap_year_df.rename(columns={'Depth': 'rainfall_amount_inches'}, inplace=True)
    avg_year_storm_shifted_leap_year_df.to_excel(writer, sheet_name=avg_year_storm_shifted_sheet_name)

    storms_sheet_name = "Summary"
    storms_df = pd.read_excel(design_storm_spreadsheet, sheet_name=storms_sheet_name)
    storm_data = storms_df.itertuples()

    print("Create hdf5 store")
    with pd.HDFStore(output_hdf5) as hdf5store:
        for storm in storm_data:
            print(storm.StormName)
            if storm.EventOnly == "YES":
                storm_df = pd.read_excel(design_storm_spreadsheet, sheet_name=storm.Sheet, usecols=['Date', 'Depth'], index_col="Date", header=0)
                storm_df.index = storm_df.index.round(freq='min')
                storm_df.rename(columns = {'Depth':'rainfall_amount_inches'}, inplace=True)
                if storm.EventStart.year%4 == 1:
                    average_year_storm_df = avg_year_storm_shifted_leap_year_df.copy(deep=True)
                    start_year = 2005
                else:
                    average_year_storm_df = avg_year_storm_shifted_df.copy(deep=True)
                    start_year = 2000

                shift = storm.EventStart.year - start_year
                shifted_avg_year_storm_df = average_year_storm_df.shift(freq=pd.DateOffset(years=shift))
                full_storm_df = pd.concat([storm_df, shifted_avg_year_storm_df])
            elif storm.EventOnly == "NO":
                full_storm_df = pd.read_excel(design_storm_spreadsheet, sheet_name=storm.Sheet, usecols=['Date', 'Depth'], index_col="Date", header=0)
                full_storm_df.index = full_storm_df.index.round(freq='min')
                full_storm_df.rename(columns = {'Depth':'rainfall_amount_inches'}, inplace=True)
            full_storm_df = full_storm_df.sort_index()
            full_storm_df.to_excel(writer, sheet_name=storm.StormName)
            precipitation_gage = PrecipitationGage(1)
            precipitation_gage.write_virtual_data_to_hdfstore(hdf5store, full_storm_df, storm.TSNumber, compress_output=False)

        print('Evap')
        evap = EvaporationStation()
        evap.read_evap_from_csv(evap_csv)
        evap.evap.index = evap.evap.index.round(freq='D')
        evap.evap.to_excel(writer, sheet_name="Evap")
        evap.write_evap_data_to_hdfstore(hdf5store, evap.evap, compress_output=False)