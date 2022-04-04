from met_data.businessclasses.precipitation_gage import PrecipitationGage
from met_data.businessclasses.evaporation import EvaporationStation
from wdmtoolbox import wdmtoolbox

# input_wdm =  r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\Woods\Calibration\sim\HSPF\input_old.wdm"
output_wdm = r"C:\Temp\MetData5new_2_01_2022.wdm"
evap_csv = r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\HSPF\evap.csv"
evap_dsn = 2

start_date = '1976-10-01 00:00:00'
end_date = '2022-02-01 00:00:00'
interval = 5
daypart = 'minute'
#daypart = 'hour'

precipitation_gages = []
fill_data = {}

fill_data[4] = (43.2, [172, 161, 121])
fill_data[10] = (49.1, [214, 64])
fill_data[64] = (49.3, [10, 214])
fill_data[121] = (49.0, [173, 204])
fill_data[160] = (47.1, [82, 193, 121])
fill_data[161] = (44.3, [172, 192, 4, 10])
fill_data[164] = (46.0, [173, 1, 121])
# fill_data[172] = (43.4, [4, 161])
fill_data[172] = (43.4, [89, 311, 4, 161]) # Which one is used?
fill_data[173] = (49.1, [121, 164])
fill_data[192] = (50.0, [173, 121, 164])
fill_data[193] = (46.2, [121, 160])
fill_data[204] = (43.9, [117, 121])
fill_data[214] = (48.0, [10, 64, 121])
fill_data[227] = (43.4, [10, 172, 4])
fill_data[234] = (43.4, [10, 172, 4])
fill_data[311] = (43.4, [172, 89, 4, 161])  # TODO long term volume
fill_data[89] = (43.4, [172, 311, 4, 161])  # TODO long term volume

h2_numbers = fill_data.keys()

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
    gage.get_raw_precipitation_data(start_date, end_date, interval, daypart)

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