from met_data.businessclasses.precipitation_gage import PrecipitationGage
from wdmtoolbox import wdmtoolbox
import pandas as pd
import datetime

input_wdm = r"C:\Temp\MetWestSide_Filled.wdm"
h2_number = 10
output_all_txt = r"C:\Temp\RG" + str(h2_number) + "all" + ".txt"
output_txt = r"C:\Temp\RG" + str(h2_number) + ".txt"
output_xlsx = r"C:\Temp\RG" + str(h2_number) + ".xlsx"
output_compressed_zeros_xlsx = r"C:\Temp\RG" + str(h2_number) + "with_zeros" + ".xlsx"

beg_date = datetime.datetime(1976, 10, 1)
end_date = datetime.datetime(2021, 10, 1)

filled_data = wdmtoolbox.extract(input_wdm, h2_number)
filled_data = filled_data.loc[beg_date:end_date]
filled_data.columns = ["Rain_Inches"]
filled_data.index.rename('Date_Time', inplace=True)
filled_data_no_na = filled_data.fillna(0)

first_data = True
compressed_data = []
first_zero_rainfall_row = None
last_zero_rainfall_row = None
for data in filled_data_no_na.itertuples():
    if first_data:
        current_rainfall = data.Rain_Inches
        if current_rainfall > 0:
            compressed_data.append(data)
            first_zero_rainfall_row = None
        else:
            first_zero_rainfall_row = data
        first_data = False
    else:
        current_rainfall = data.Rain_Inches
        if current_rainfall > 0:
            if first_zero_rainfall_row is None:
                compressed_data.append(data)
            elif first_zero_rainfall_row is not None and last_zero_rainfall_row is None:
                compressed_data.append(first_zero_rainfall_row)
                compressed_data.append(data)
                first_zero_rainfall_row = None
            elif first_zero_rainfall_row is not None and last_zero_rainfall_row is not None:
                compressed_data.append(first_zero_rainfall_row)
                compressed_data.append(last_zero_rainfall_row)
                compressed_data.append(data)
                first_zero_rainfall_row = None
                last_zero_rainfall_row = None
            else:
                print("Logic issue 1")
        elif current_rainfall == 0 and first_zero_rainfall_row is None:
            first_zero_rainfall_row = data
        elif current_rainfall == 0 and first_zero_rainfall_row is not None:
            last_zero_rainfall_row = data
        else:
            print("Logic issue 2")
filled_data_compressed_zeros = pd.DataFrame(compressed_data)
filled_data_compressed_zeros = filled_data_compressed_zeros.set_index('Index')
filled_data_compressed_zeros.index.rename('Date_Time', inplace=True)

# filled_data_no_na.to_csv(output_all_txt, date_format="%m/%d/%Y %H:%M", sep=" ", float_format="%.5f", quoting=csv.QUOTE_NONE, escapechar=" ")
try:
    filled_data_no_na.to_excel(output_xlsx, float_format="%.6f")
except:
    print ("Data with zeros too large. Dropping zeros.")
    filled_data.dropna().to_excel(output_xlsx, float_format="%.6f")
filled_data_compressed_zeros.to_excel(output_compressed_zeros_xlsx,  float_format="%.6f")
