from wdmtoolbox import wdmtoolbox
import pandas as pd

wdm = r"C:\Temp\MetWestSide - Copy.wdm"
rf_avg_xls = r"C:\Temp\rfavga18.xlsx"
longterm_active = [1004, 1010, 1014, 1153, 1002, 1003] #Long term active gages

longterm_inactive_1984 = [1311]
longterm_inactive_1999 = [1130]
longterm_inactive_2003 = [1147]
longterm_inactive_2017 = [1058]
active_after_84 = [1121]
active_after_91 = [1064]
active_after_95 = [1001]
active_after_00 = [1160, 1117, 1161, 1164]
active_after_02 = [1173, 1172]
active_after_05 = [1192, 1193]
active_after_07 = [1204]
active_after_10 = [1214, 1082]
active_after_18 = [1230, 1227, 1234]

rgs = longterm_active + active_after_84 + active_after_91 + active_after_95 + active_after_00 + active_after_02 +\
      active_after_05 + active_after_07 + active_after_10 + active_after_18

# read dsns
rg_data = []
for rg in rgs:
    rg_data.append(wdmtoolbox.extract(wdm, rg))

# concatenate data sets
rg_df = pd.concat(rg_data, axis=1)

# drop na's
rg_df_no_na = rg_df.dropna()

# sum values
avg_df = rg_df_no_na.mean()

# write to excel
avg_df.to_excel(rf_avg_xls)
