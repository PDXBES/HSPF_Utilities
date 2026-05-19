from met_data.businessclasses.precipitation_gage import PrecipitationGage
import pandas as pd
from met_data.businessclasses.evaporation import EvaporationStation
from wdmtoolbox import wdmtoolbox

output_wdm = r"C:\Temp\DesignStorm5min.wdm"
design_storm_spreadsheet = r'V:\HydroModHSPF\DesignStorms\DesignStorms.xlsx'
#design_storm_check_spreadsheet = r'C:\Users\sgould\Desktop\CST\DesignStormsCheck.xlsx'
#avg_year_csv = r'C:\Users\sgould\Desktop\CST\AvgYear.csv'
evap_dsn = 9999
evap_csv = r"\\BESFile1\ASM_Projects\HydroModHSPF\Evap\evap.csv"
interval = 5
daypart = 'minute'

print("Create wdm")
wdmtoolbox.createnewwdm(output_wdm, True)

#
# # avg year rainfall
avg_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="AvgYr5min", names=['Date', "Depth"], index_col="Date", header=0)
avg_year_storm.index = avg_year_storm.index.round(freq='min')

PrecipitationGage.write_design_storm_to_wdm(output_wdm, 1999, 'AvgYr', 2, 5, avg_year_storm)

avg_year_storm_2002 = avg_year_storm.copy(deep=True)
avg_year_storm_2002 = avg_year_storm_2002.shift(freq=pd.DateOffset(years=2))

avg_year_storm_2005 = avg_year_storm.copy(deep=True)
avg_year_storm_2005 = avg_year_storm_2005.shift(freq=pd.DateOffset(years=5))

avg_year_storm_2010 = avg_year_storm.copy(deep=True)
avg_year_storm_2010 = avg_year_storm_2010.shift(freq=pd.DateOffset(years=10))

avg_year_storm_2025 = avg_year_storm.copy(deep=True)
avg_year_storm_2025 = avg_year_storm_2025.shift(freq=pd.DateOffset(years=25))

# wq storm
wq = pd.read_excel(design_storm_spreadsheet, sheet_name="WQ", names=['Date', "Depth"], index_col="Date", header=0)
wq = avg_year_storm.append(wq)
wq.index = wq.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2000, 'SCS24hrWQ', 2, 5, wq)

# 2 year storm
scs24hr_2_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="2_24hr", names=['Date', "Depth"],
                                     index_col="Date", header=0)
scs24hr_2_year_storm = avg_year_storm.append(scs24hr_2_year_storm)
scs24hr_2_year_storm.index = scs24hr_2_year_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2002, 'SCS24hr2yr', 2, 5, scs24hr_2_year_storm)
test = wdmtoolbox.extract(output_wdm, 2002)

# 5 year storm
scs24hr_5_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="5_24hr", names=['Date', "Depth"],
                                     index_col="Date", header=0)
scs24hr_5_year_storm = avg_year_storm.append(scs24hr_5_year_storm)
scs24hr_5_year_storm.index = scs24hr_5_year_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2005, 'SCS24hr5yr', 2, 5, scs24hr_5_year_storm)

# 10 year storm
scs24hr_10_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="10_24hr", names=['Date', "Depth"],
                                      index_col="Date", header=0)
scs24hr_10_year_storm = avg_year_storm.append(scs24hr_10_year_storm)
scs24hr_10_year_storm.index = scs24hr_10_year_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2010, 'SCS24hr10yr', 2, 5, scs24hr_10_year_storm)

# 25 year storm
scs24hr_25_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="25_24hr", names=['Date', "Depth"],
                                      index_col="Date", header=0)
scs24hr_25_year_storm = avg_year_storm.append(scs24hr_25_year_storm)
scs24hr_25_year_storm.index = scs24hr_25_year_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2025, 'SCS24hr25yr', 2, 5, scs24hr_25_year_storm)

# 100 year storm
scs24hr_100_year_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="100_24hr", names=['Date', "Depth"],
                                       index_col="Date", header=0)
scs24hr_100_year_storm = avg_year_storm.append(scs24hr_100_year_storm)
scs24hr_100_year_storm.index = scs24hr_100_year_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2100, 'SCS24hr100yr', 2, 5, scs24hr_100_year_storm)

# 2 year 6hrstorm
D_2_year_6hr_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="2_6hr", names=['Date', "Depth"],
                                     index_col="Date", header=0)
D_2_year_6hr_storm = avg_year_storm_2002.append(D_2_year_6hr_storm)
D_2_year_6hr_storm.index = D_2_year_6hr_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2008, '2_6hr', 2, 5, D_2_year_6hr_storm)

# 5 year storm
D_5_year_6hr_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="5_6hr", names=['Date', "Depth"],
                                     index_col="Date", header=0)
D_5_year_6hr_storm = avg_year_storm_2005.append(D_5_year_6hr_storm)
D_5_year_6hr_storm.index = D_5_year_6hr_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2011, 'D05yr6h', 2, 5, D_5_year_6hr_storm)

# 10 year storm
D_10_year_6hr_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="10_6hr", names=['Date', "Depth"],
                                      index_col="Date", header=0)
D_10_year_6hr_storm = avg_year_storm_2010.append(D_10_year_6hr_storm)
D_10_year_6hr_storm.index = D_10_year_6hr_storm.index.round(freq='min')
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2016, 'D10yr6h', 2, 5, D_10_year_6hr_storm)

# 25 year storm
D_25_year_6hr_storm = pd.read_excel(design_storm_spreadsheet, sheet_name="25_6hr", names=['Date', "Depth"],
                                      index_col="Date", header=0)
D_25_year_6hr_storm = avg_year_storm_2025.append(D_25_year_6hr_storm)
D_25_year_6hr_storm.index = D_25_year_6hr_storm.index.round(freq='min')
# D_25_year_6hr_storm =D_25_year_6hr_storm.shift(freq=pd.DateOffset(minutes=-5))
D_25_year_6hr_storm.to_excel(r"c:\temp\d25.xlsx")
PrecipitationGage.write_design_storm_to_wdm(output_wdm, 2031, 'D25yr6h', 2, 5, D_25_year_6hr_storm)
wdm_25 = wdmtoolbox.extract(output_wdm, 2031)
wdm_25.to_excel(r"c:\temp\from_wdm_d25.xlsx")

evap = EvaporationStation()
evap.read_evap_from_csv(evap_csv)
evap.write_evaporation(output_wdm, evap_dsn)
pass