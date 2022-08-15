from met_data.businessclasses.precipitation_gage import PrecipitationGage
from met_data.businessclasses.evaporation import EvaporationStation
from wdmtoolbox import wdmtoolbox

# input_wdm =  r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\Woods\Calibration\sim\HSPF\input_old.wdm"
input_wdm = r"C:\Temp\MetWestSide.wdm"
output_wdm = r"C:\Temp\MetWestSide_Filled.wdm"
evap_csv = r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\HSPF\evap.csv"
evap_dsn = 9999

start_date = '1976-04-01 00:00:00'
end_date = '2022-04-05 00:00:00'
interval = 5
daypart = 'minute'
#daypart = 'hour'

precipitation_gages = []
fill_data = {}

fill_data[2] = (1.0558, [147, 130, 82, 58, 153])
fill_data[3] = (1.0709, [147, 130, 82, 58, 153])
fill_data[4] = (1.0000, [172, 161, 10])
# fill_data[6] = (46.2 , [])
fill_data[10] = (1.1106, [214, 64, 14, 4])
# fill_data[12] = (46.2 , [])
fill_data[14] = (1.0557, [10, 4])
fill_data[58] = (1.0, [121, 193, 160, 153, 10, 4])
fill_data[153] = (0.9775, [58, 10, 4])
# fill_data[145] = (46.2, [])

fill_data[1] = (1.0514, [10, 4])
fill_data[130] = (1.0034, [10, 4])
fill_data[147] = (1.0795, [10, 4])
#fill_data[167] = (46.2, [10, 4])
fill_data[82] = (0.9919, [10, 4])
fill_data[117] = (0.9587, [10, 4])
fill_data[64] = (1.1066, [10, 227, 214, 14])
fill_data[121] = (1.0969, [173, 204, 58, 153])
fill_data[160] = (1.0602, [82, 193, 121, 58, 153])
fill_data[161] = (1.0006, [172, 192, 4, 10])
fill_data[164] = (1.0306, [173, 1, 121])
fill_data[172] = (0.9882, [89, 311, 4, 161, 10])
fill_data[173] = (1.1093, [121, 164])
fill_data[192] = (1.1423, [173, 121, 164, 10, 4])
fill_data[193] = (1.0407, [121, 160, 58, 153, 10, 4])
fill_data[204] = (0.9891, [117, 121])
fill_data[214] = (1.0846, [10, 64, 121, 58, 153])
fill_data[227] = (1.0, [10, 172, 4]) #Short record
fill_data[234] = (1.0015, [10, 172, 4]) #Short record
fill_data[311] = (1.0846, [172, 89, 4, 161])
fill_data[89] = (0.9794, [172, 311, 4, 161])

h2_numbers = fill_data.keys()

h2 = []
for gage in fill_data.keys():
    h2 = h2 + fill_data[gage][1]
fill_h2 = set(h2)
for fill in fill_h2:
    if not fill in h2_numbers:
        print(fill)
# h2_numbers = [230, 125]
for h2_number in h2_numbers:
    precipitation_gages.append(PrecipitationGage(h2_number))

for gage in precipitation_gages:
    gage.long_term_avg = fill_data[gage.h2_number][0]
    for h2_number in fill_data[gage.h2_number][1]:
        for fill_gage in precipitation_gages:
            if fill_gage.h2_number == h2_number:
                gage.alternative_gages.append(fill_gage)

print("getting raw data")
for gage in precipitation_gages:
    print(gage.h2_number)
    # raw_data = wdmtoolbox.extract(input_wdm, gage.h2_number + 1000)
    # raw_data.columns.values[0] = "rainfall_amount_inches"
    # gage.raw_data = raw_data
    gage.get_raw_precipitation_data(start_date, end_date, interval, daypart)
    pass

print("filling data")
for gage in precipitation_gages:
    print(gage.h2_number)
    gage.fill_precipitation_data()

print("Create wdm")
wdmtoolbox.createnewwdm(output_wdm, True)

print("Writing raw data")
for gage in precipitation_gages:
    gage.write_raw_data_to_wdm(output_wdm, 2, 5)
    gage.write_filled_data_to_wdm(output_wdm, 2, 5)


evap = EvaporationStation()
evap.read_evap_from_csv(evap_csv)
evap.write_evaporation(output_wdm, evap_dsn)

pass