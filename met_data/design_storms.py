from met_data.businessclasses.precipitation_gage import PrecipitationGage
import pandas as pd
from met_data.businessclasses.evaporation import EvaporationStation
from wdmtoolbox import wdmtoolbox

input_wdm = r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\Woods\Calibration\sim\HSPF\input_old.wdm"
# output_wdm = r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\Woods\Calibration\sim\HSPF\design_storm_input.wdm"
output_wdm = r"C:\Temp\HSPFWorkshopMaterials\HSPFData\DesignStorm5min.wdm"
design_storm_spreadsheet = r'C:\Users\sgould\Desktop\CST\DesignStorms.xlsx'
design_storm_check_spreadsheet = r'C:\Users\sgould\Desktop\CST\DesignStormsCheck.xlsx'
avg_year_csv = r'C:\Users\sgould\Desktop\CST\AvgYear.csv'
evap_dsn = 2
evap_csv = r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\HSPF\evap.csv"
interval = 5
daypart = 'minute'

print("Create wdm")
wdmtoolbox.createnewwdm(output_wdm, True)

#
# # avg year rainfall
avg_year_storm = pd.read_csv(avg_year_csv, index_col="Date", usecols=["Date", "Depth"],  header=0, parse_dates=True)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 1999, 'AvgYr', 2, 5, avg_year_storm)

# wq storm
wq = pd.read_excel(design_storm_spreadsheet, sheet_name="WQ", names=['Date', "Depth"], index_col="Date", header=0)
wq = avg_year_storm.append(wq)
wq.to_excel(design_storm_check_spreadsheet)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2000, 'SCS24hrWQ', 2, 5, wq)

# 2 year storm
scs24hr_2_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="2", names=['Date', "Depth"],
                                     index_col="Date", header=0)
scs24hr_2_year_storm = avg_year_storm.append(scs24hr_2_year_storm)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2002, 'SCS24hr2yr', 2, 5, scs24hr_2_year_storm)

# 5 year storm
scs24hr_5_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="5", names=['Date', "Depth"],
                                     index_col="Date", header=0)
scs24hr_5_year_storm = avg_year_storm.append(scs24hr_5_year_storm)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2005, 'SCS24hr5yr', 2, 5, scs24hr_5_year_storm)

# 10 year storm
scs24hr_10_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="10", names=['Date', "Depth"],
                                      index_col="Date", header=0)
scs24hr_10_year_storm = avg_year_storm.append(scs24hr_10_year_storm)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2010, 'SCS24hr10yr', 2, 5, scs24hr_10_year_storm)

# 25 year storm
scs24hr_25_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="25", names=['Date', "Depth"],
                                      index_col="Date", header=0)
scs24hr_25_year_storm = avg_year_storm.append(scs24hr_25_year_storm)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2025, 'SCS24hr25yr', 2, 5, scs24hr_25_year_storm)

# 100 year storm
scs24hr_100_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="100", names=['Date', "Depth"],
                                       index_col="Date", header=0)
scs24hr_100_year_storm = avg_year_storm.append(scs24hr_100_year_storm)
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2100, 'SCS24hr100yr', 2, 5, scs24hr_100_year_storm)

evap = EvaporationStation()
evap.read_evap_from_csv(evap_csv)
evap.write_evaporation(output_wdm, 2)
pass