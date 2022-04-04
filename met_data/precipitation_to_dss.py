from met_data.businessclasses.precipitation_gage import PrecipitationGage
from met_data.businessclasses.evaporation import EvaporationStation
from wdmtoolbox import wdmtoolbox
from flow_data.dataio.base_data_io import BaseDataIo

# input_wdm =  r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\Woods\Calibration\sim\HSPF\input_old.wdm"
output_wdm = r"C:\Temp\MetData5new_11_27_2021_cal.wdm"
dss_file_path = r"C:\Temp\Tryon.dss"

start_date = '1976-10-01 00:00:00'
end_date = '2021-11-18 00:00:00'
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

basin_name = { 4: ("South Ash", "Sylvania PCC"),
              10: ("Tryon", "Collins View School"),
              64: ("West Lents", "Harney Pump Station"),
             121: ("Guilds Lake", "Yeon Pump Station"),
             160: ("St Johns C", "WPCL"),
             161: ("Sylvan", "Sylvan School"),
             164: ("Mill Jefferson", "SW 12th & Clay"),
             172: ("Fanno", "Maplewood Elementary School"),
             173: ("Tanner B", "Metro Learning Center"),
             192: ("Tanner A", "Children's Museum"),
             193: ("Fiske B ", "Astor School"),
             204: ("Balch", "Swan Island CSO Pump Station"),
             214: ("California", "OPB Raingage"),
             227: ("Stephens", "Wilson School"),
             234: ("Tryon", "Fire Station 18 Rain Gauge"),
             311: ("Fanno", "Bridlemile School"),
             89: ("Fanno", "Vermont Hills Pump Station")}

h2_numbers = fill_data.keys()

for h2_number in h2_numbers:
    precipitation_gages.append(PrecipitationGage(h2_number))

rain_gage_for_dss = [4, 172, 311, 89, 10, 234, 227, 214]

for gage in precipitation_gages:
    gage.long_term_avg = fill_data[gage.h2_number][0]
    for h2_number in fill_data[gage.h2_number][1]:
        for fill_gage in precipitation_gages:
            if fill_gage.h2_number == h2_number:
                gage.alternative_gages.append(fill_gage)

print("reading data")
data_io = BaseDataIo()
for gage in precipitation_gages:
    if gage.h2_number in rain_gage_for_dss:
        gage.read_raw_data_from_wdm(output_wdm)
        gage.read_filled_data_from_wdm(output_wdm)
        path_name = "/" + basin_name[gage.h2_number][0] + "/" + str(gage.h2_number) + " " + basin_name[gage.h2_number][1] + "/PREC//5MIN/FILLED/"
        data_io.write_5_minute_precipitation_dss(dss_file_path, path_name, gage.filled_data.fillna(0))
        path_name = "/" + basin_name[gage.h2_number][0] + "/" + str(gage.h2_number) + " " + basin_name[gage.h2_number][1] + "/PREC//5MIN/RAW/"
        data_io.write_5_minute_precipitation_dss(dss_file_path, path_name, gage.raw_data)
