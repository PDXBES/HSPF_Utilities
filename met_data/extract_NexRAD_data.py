import datetime
import os
import tarfile
from datetime import datetime, timezone, timedelta


def level3_nexrad_extraction(key_word, tar):
    names = []
    for tarinfo in tar.getmembers():
        if key_word in tarinfo.name:
            names.append(tarinfo)
    return names


def instantaneous_precip_rate_files(tar):
    key_word = "DPR" #p176
    return level3_nexrad_extraction(key_word, tar)


def digital_precipitation_array_files(tar):
    key_word = "DPA" #p81
    return level3_nexrad_extraction(key_word, tar)


def hourly_precipipitation_files(tar):
    key_word = "N1P" #p78
    return level3_nexrad_extraction(key_word, tar)




#keyword = N1P  1 hour precipitation #p78
#keyword = DPA  1 hour Digital precipitation array #p81


# def tar_dir(path, working_path, filename):
#     filepath = path + "\\" + filename
#     tar = tarfile.open(filepath, 'r:gz')
#     tar.extractall(working_path)

tar_folder_path = r"D:\_HAS012243254"
tar_folder_working_path_dpa = r"C:\Users\sggho\Desktop\NexRAD_raw\workingDPA"
tar_folder_working_path_n1p = r"C:\Users\sggho\Desktop\NexRAD_raw\workingN1P"
tar_folder_working_path = r"C:\Users\sggho\Desktop\NexRAD_raw\working1"
# tar_file_name = r"NWS_NEXRAD_NXL3_KRTX_20220103000000_20220103235959.tar.gz"

# loop through targz files in folder
with os.scandir(tar_folder_path) as dirs:
    for entry in dirs:
#        if entry.name[-6:len(entry.name)] == "tar.gz":
        if entry.name[-6:len(entry.name)] == "tar.gz":
            print("Extracting: " + entry.name + " To: " + tar_folder_working_path)
            try:
                # tar = tarfile.open(tar_folder_path + "\\" + entry.name, 'r:gz')
                tar = tarfile.open(tar_folder_path + "\\" + entry.name, 'r:gz')
                try:
                    tar.extractall(tar_folder_working_path, members=instantaneous_precip_rate_files(tar))
                except:
                    print("could not extract p176")
                try:
                    tar.extractall(tar_folder_working_path_n1p, members=hourly_precipipitation_files(tar))
                except:
                    print("could not extract p78")
                try:
                    tar.extractall(tar_folder_working_path_dpa, members=digital_precipitation_array_files(tar))
                except:
                    print("could not extract p81")
            except:
                print("******************* Could not extract from: " + tar_folder_path + "\\" + entry.name)
        else:
            print("**** Unknown File Extension file not extracted: " + entry.name)


# begin_time = datetime(2022, 1, 3, hour=12)
# stop_time = datetime(2022, 1, 5)
# begin_time_utc = begin_time + timedelta(hours=8)
# stop_time_utc = stop_time + timedelta(hours=8)
# start_time_utc_int = begin_time_utc.strftime("%Y%m%d%H%M")
# stop_time_utc_int = stop_time_utc.strftime("%Y%m%d%H%M")
# with os.scandir(tar_folder_working_path) as dirs:
#     for entry in dirs:
#         if start_time_utc_int <= entry.name[-12:len(entry.name)] and stop_time_utc_int >= entry.name[-12:len(entry.name)]:
#             print(entry.name)

# get all filenames in folder
# sort by last 12 characters
    # def get_time(file_name):
    #    time = file_name[-12:-1]
    #    return time
    # filenames.sort(key=get_time)
    # loop through files
        # get date from last 12 characters name[-12] 202201032149
        # check if between start and end date and add copy to working directory
