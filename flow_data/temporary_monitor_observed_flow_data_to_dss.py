from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from flow_data.dataio.base_data_io import BaseDataIo

#                   Saltzmann
#                   6799 AMM001 QAQC

#                   Council Crest
#                   Ivey
#                   13838 Dosch road
#                   6460 QAQC not sure why this gage backwaters?
#                   Unnamed 2
#                   13837 SW Boundary St

#                   Stephens
#                                   10310 ACS422 Greater Portland Bible Church
#                   6442 ACS400 # This gage tends to over predict volume not sure how to qaqc
#                   4849 ACS613 # QAQC 5/31/2006 - 10/13/2014 Data quality better from WY 2010 onward
#                                   6444 AMX092 # 9/28/2009 - 10/12/2010 This gage has significant depth and velocity issues
#                   6441 ACY343 # QAQC 10/9/2009 - 10/12/2010 noticeable shift in data after 1/1/2010
#                   13706 ACY344 # QAQC 11/27/2019 Flodar
#                                   6443 QAQC ACY337 10/5/2009 - 10/12/2010
#                   3472 ACY443 # QAQC 8/28/2002 - 9/20/2004

#location_ids = [10310, 6442, 4849, 6441, 13706, 6443, 34722, 13706]
                    #Tryon
# 9072 ACX033 QAQC                      10370  ACX227 QAQC
#                   10373 ACX451 QAQC Not sure why data is not valid after March 2020
#                   10372 ACX345 QAQC
#                                    10371  ANL866 QAQC
#                   10357 ADC775 QAQC
# Falling
#               10359 ADD143 10358 QAQC
#                   6790 ADH086
# Arnold Creek      5635 ADK834
#                   4296 ADK773
#                  USGS14211315


#location_ids = [9072]

# Woods (QA\QC)
#                           10294 Trib
#               10519 ADC182 # issues with depth sensor 2020-01-09 swapped to ultrasonic on 2020-02-25
#location_ids = [10294]

# South Ash (QA/QC)
# 5367 ADJ264 # depth/velocity switched? Changed to ultrasonic depth sensor in March 2019
# 10497 ADF622 # significant difference between submerged depth sensor and u sonic depth sensor installed in March 2019

# Fanno
# 1289 wq?
#                   3472 ACY443 # 8/28/2002 - 9/20/2004

begin = '2007-04-1'
end = '2021-11-29'
minimum_depth = 0.8
maximum_depth = 1000
minimum_velocity = 0
maximum_velocity = 1000

all_filter_dates = {
    # Council Crest (Snow February 11-15 2021 Melt through 20th? )
                13838:
                [('2021-01-26 14:00', '2021-01-30 08:00'),
                 ('2021-01-30 17:00', '2021-02-05 10:00'),
                 ('2021-02-22 12:00', '2021-03-05 00:00'),
                 ('2021-03-05 01:00', '2021-03-17 12:00'),
                 ('2021-03-21', '2021-03-25 10:00'),
                 ('2021-03-28 12:00', '2021-03-31'),
                 ('2021-06-11 06:00', '2021-06-15 16:00'),
                 ('2021-09-17 22:00', '2021-09-20 0:00'),
                 ('2021-09-27 1:00', '2021-10-21'),
                 ('2021-10-21', '2021-11-17')], # '2021-06-15 16:00')],
    # ,'2021-10-01')],
    # Council Crest
                13837:
                [('2021-01-21', '2021-02-03 1:15'),
                 ('2021-02-03 1:50', '2021-02-22 00:00'),
                 ('2021-02-22 12:00', '2021-07-01 00:00'),
                 ('2021-09-01', '2021-10-14'),
                 ('2021-10-14', '2021-10-30 4:00'),
                 ('2021-10-30 7:00', '2021-11-17')],
    # Ivey Creek
                6460:
                [('2009-10-01', '2009-11-13'),
                 ('2009-11-17', '2009-12-04'),
                 ('2009-12-12', '2009-12-16'),
                 ('2009-12-19', '2009-12-25'),
                 ('2009-12-27', '2009-12-28'),
                 ('2009-12-30', '2010-10-1')],
    # Bible Church
                10310:
                [('2018-04-09', '2020-10-16')],
    # Fanno
                3472:
                [('2002-08-28', '2002-12-14'),
                 ('2002-12-24', '2004-01-27'),
                 ('2004-02-06', '2004-09-20')],
    # Stephens Trib
                6443:
                [('2009-10-09', '2010-02-02'),
                 ('2010-02-10', '2010-09-25'),
                 ('2010-09-26 08:00', '2010-10-12')],
    # Stephens Taylor Ferry
                13706:
                [('2019-11-27', '2021-09-30')],
    # Stephens Taylor Ferry Old
                6441:
                [('2009-10-09', '2010-06-06')],
    # # Stephens Trib
                6444:
                [('2009-09-28', '2010-10-12')],
    # Stephens below Fredmeyer
                4849:
                [('2006-11-09', '2008-07-12'),
                 ('2008-08-06', '2009-01-11'),
                 ('2009-01-13', '2010-07-08'),
                 ('2010-09-07', '2010-10-10'),
                 ('2010-10-22', '2011-10-22'),
                 ('2011-10-24', '2014-10-13')],
    # Stephens above Fredmeyer
                6442:
                [('2009-10-01', '2010-01-02 00:00'),
                 ('2010-01-05 20:00', '2010-02-09'),
                 ('2010-03-15', '2010-03-26 06:00'),
                 ('2010-03-26 23:00', '2010-03-28 07:00'),
                 ('2010-03-29 00:00', '2010-04-02 9:00'),
                 ('2010-04-08 12:00', '2010-06-10 08:00'),
                 ('2010-06-10 21:00', '2010-10-01'),

                 ('2020-06-10', '2020-09-22'),
                 ('2020-09-22', '2021-04-30')],

    # Saltzman Creek ('2010-11-17', '2012-10-12'),
                6799:
                [
                 ('2012-10-12', '2012-11-29'),
                 ('2012-12-11 12:00', '2013-06-17'),
                 ('2013-06-19', '2013-06-30'),
                 ('2013-08-17', '2013-12-06'),
                 ('2013-12-11', '2014-01-28'),
                 ('2014-02-11', '2014-02-16'),
                 ('2014-02-18 12:00', '2014-03-04'),
                 ('2014-03-06', '2015-04-27')],
    # Tryon
                9072:
                [('2017-05-1', '2018-11-21'),
                 ('2019-02-09', '2019-11-21'),
                 ('2019-11-25', '2020-02-02'),
                 ('2020-02-15', '2020-09-22'),
                 ('2020-09-22', '2021-01-12 20:30'),
                 ('2021-01-13 00:30', '2021-10-01')],

                10370: # Removed 9/17 2021
                [('2018-06-01', '2018-06-09'),
                 ('2018-06-10', '2018-09-16'),
                 ('2018-11-03', '2018-11-25'),
                 ('2018-11-29', '2018-12-16'),
                 ('2018-12-22', '2020-06-06'),
                 ('2020-07-17', '2020-09-22'),
                 ('2020-09-22', '2021-6-15')],

                10373:
                [('2018-05-01', '2018-06-06'),
                 ('2018-06-09', '2018-08-11'),
                 ('2018-09-06', '2018-09-08'),
                 ('2018-09-11', '2018-09-25'),
                 ('2018-10-02', '2019-06-04'),
                 ('2019-07-10', '2019-08-10'),
                 ('2019-08-20', '2019-09-03 00:00'),
                 # ('2019-09-03 00:00', '2019-10-03 00:00'), # looks like velocity is high?
                 ('2019-10-03 00:00', '2020-07-25'),
                 ('2020-08-06', '2020-08-07'),
                 ('2020-08-21', '2020-08-22'),
                 ('2020-09-15', '2021-02-25'),
                 # ('2021-02-25', '2021-06-15'), # depth sensor issues
                 ('2021-06-15', '2021-07-15'),
                 ('2021-09-17', '2021-10-14')],

                13833: # Blockage downstream of monitor
                [('2021-01-01', '2021-02-21 10:00'),
                 ('2021-02-22 12:00', '2021-03-10'),
                 ('2021-03-20 13:00', '2021-03-24'),
                 ('2021-03-28 13:00', '2021-03-29'),
                 ('2021-04-24 4:00', '2021-04-24 18:00'),
                 ('2021-09-18 0:00', '2021-09-18 15:00'),
                 ('2021-09-18 23:00', '2021-09-19 3:00'),
                 ('2021-09-19 03:35', '2021-09-19 07:00'),
                 ('2021-09-19 12:40', '2021-09-19 17:00')],
                 #('2021-09-18 07:30', '2021-09-19 07:30')],

                10372:
                [('2018-05-01', '2019-10-16'),
                 ('2019-10-28', '2019-11-17'),
                 ('2019-11-28', '2019-12-06'),
                 ('2020-01-07', '2020-01-25'),
                 ('2020-02-12', '2020-07-01'),
                 ('2020-07-01', '2020-09-01'),
                 ('2020-09-11', '2021-01-02'),
                 ('2021-01-12 19:00', '2021-04-30'),
                 ('2021-04-30', '2021-10-14')], # 2021-01-04 to 2021-01-11 blockage?

                10371: # Gage removed 2021-06-15
                [('2018-05-01', '2018-12-01'),
                 ('2019-02-28', '2019-05-12'),
                 ('2019-06-01', '2019-08-06'),
                 ('2019-09-12', '2019-09-15'),
                 ('2019-09-18', '2019-12-20'),
                 ('2019-12-22', '2020-07-12'),
                 ('2020-09-17', '2020-09-23 18:00'),
                 ('2020-09-24 21:00', '2020-09-26 8:00'),
                 ('2020-09-30 8:00', '2021-04-30'),
                 # ('2021-06-12', '2021-10-14')
                 ],

                10357:
                [('2009-10-01', '2018-11-09'),
                 ('2018-11-21', '2019-08-26'),
                 ('2019-09-07', '2020-06-08'),
                 ('2020-07-08', '2020-09-02'),
                 ('2020-09-05', '2020-09-22'),
                 ('2020-09-22', '2021-01-20 00:00'),
                 ('2021-01-22 00:00', '2021-10-14')],
    # Falling
                13823: #Still waiting on 2021-10-11 data could clean up a few things in the earlier data
                [('2020-12-01', '2021-06-15'),
                 ('2021-06-15', '2021-10-14')],

                10359: # blockage after late January event
                [('2007-05-01', '2018-10-20'),
                 ('2018-10-24', '2018-11-10'),
                 ('2018-11-17', '2018-11-18'),
                 ('2018-11-21', '2020-07-01'),
                 ('2020-07-01', '2020-09-22'),
                 ('2020-09-22', '2021-04-30'),
                 ('2021-04-30', '2021-05-06')],

                10358:
                [('2007-05-01', '2018-07-06'),
                 ('2018-07-15', '2018-08-04'),
                 ('2018-08-23', '2018-08-28'),
                 ('2018-09-12', '2018-09-23'),
                 ('2018-09-30', '2018-11-20 00:00'),
                 ('2018-11-21 12:00', '2018-12-19'),
                 ('2019-01-16', '2019-02-11'),
                 ('2019-02-13', '2019-07-27'),
                 ('2019-07-31', '2019-08-06'),
                 ('2019-08-08', '2019-08-11'),
                 ('2019-09-11', '2019-11-09'),
                 ('2019-11-12', '2020-05-14'),
                 ('2020-05-16', '2020-07-20'),
                 ('2020-10-10', '2020-10-15'),
                 ('2020-12-02', '2021-04-30'),
                 ('2021-04-30', '2021-06-21')],  #Flow quality poor from 2021 6 21 to 2021 9 13
                6790:
                [('2010-10-01', '2011-10-01')],
                4296:
                [('2010-10-01', '2011-10-01')],
                5365: # 2007-4-13 to 2008-6-9 15 min
                [('2007-04-13', '2011-05-06')],
    #South Ash
                10497:
                [('2018-11-08', '2019-01-25'),
                 ('2019-03-10', '2019-03-14'),
                 ('2019-05-13 13:00', '2019-05-15 19:00'),
                 ('2019-05-16 3:00','2019-05-26 12:00'), # Data more consistent after this period
                 ('2019-06-20', '2019-07-19'),
                 ('2019-09-07 16:00', '2019-10-08 8:00'),
                 ('2019-10-16', '2019-10-16 18:00'),
                 ('2019-10-16 19:45', '2019-10-16 23:00'),
                 ('2019-10-17 3:00', '2019-10-16 23:00'),
                 ('2019-11-15', '2020-06-23'),
                 ('2020-09-18', '2020-09-18 20:00'),
                 ('2020-09-23 12:00', '2020-09-24 04:00'),
                 ('2020-09-25 6:00', '2020-09-25 22:00'),
                 ('2020-10-10 0:00', '2020-10-13 0:00'),
                 ('2020-11-03', '2021-04-12'),
                 ('2021-06-12 19:00', '2021-06-15 00:00')], #reviewed through 9/14

                5367:
                [('2007-05-29', '2019-01-12'),
                 ('2019-01-15', '2019-01-24'),
                 ('2019-03-06 16:00', '2019-04-03 0:00'),
                 ('2019-04-05 0:00', '2019-08-13'),
                 ('2019-09-08', '2019-10-10'),
                 ('2019-10-17', '2019-10-11'),
                 ('2019-11-18', '2019-12-05'),
                 ('2020-01-07 12:00', '2020-06-19'),
                 ('2020-06-19', '2020-9-2'),
                 ('2020-10-15 12:00', '2021-09-14')],

                # Woods
                # 2018-12-15 to 12-25-2018 depth is low
                # 2020-10-10 to 2020-10-14 to is high
                # Data between 2021-02-28', '2021-04-30' is suspect
                10519:
                [('2018-10-1', '2018-12-20'),
                 ('2019-01-06', '2019-01-17'),
                 ('2019-01-18', '2019-01-20 12:00'),
                 ('2019-01-24', '2019-03-10'),
                 ('2019-03-11', '2019-09-07'), #Ultrasonic Sensor
                 ('2019-09-08', '2019-11-12 17:00'),
                 ('2019-11-15 5:00', '2019-11-15 14:00'),
                 ('2019-11-17 11:00', '2019-11-17 18:00'),
                 ('2019-11-18 17:00', '2020-07-06'),
                 ('2020-08-06', '2020-08-07'),
                 ('2020-08-07', '2020-10-09 0:00'),
                 ('2020-10-10 0:00', '2020-12-18'),
                 ('2020-12-23', '2021-02-04'),
                 ('2021-02-28', '2021-09-20')],

                # 10519:
                # [('2018-10-1', '2021-08-25')],
    4283:  # BEFORE 2010-11-10 WQ
        [('2010-11-10', '2011-05-06')],
                10294:
                [('2017-10-01', '2018-2-21 10:00'),
                 ('2018-3-14', '2018-4-25'),
                 ('2018-10-5 10:00', '2018-11-3'),
                 ('2018-11-6', '2020-05-26')]
    }

location_ids = [13823, 10359, 10358, 13833] #[5365] #[9072, 10370, 10373, 10372, 10371, 10357, 6790, 4296, 4283, 5365] #5635
basin_name = "Tryon"

dss_file_path = r"C:\Temp\Tryon.dss"

data_io = BaseDataIo()
for location_id in location_ids:
        print(location_id)
        temp_monitor1 = TemporaryFlowMonitorData(location_id, True, True, True, minimum_depth=minimum_depth)
        temp_monitor1.get_raw_data(begin, end)
        temp_monitor1.get_location_data()
        node_name = temp_monitor1.location_data['manhole_hansen_id'][0]
        temp_monitor1.get_visit_data(begin, end)
        temp_monitor1.node_name = node_name
        beg_obs = temp_monitor1.raw_data.index.values[0]
        end_obs = temp_monitor1.raw_data.index.values[-1]

        temp_monitor_filtered = TemporaryFlowMonitorData(location_id, True, True, True, minimum_depth=minimum_depth,
                                                         maximum_depth=maximum_depth,
                                                         minimum_velocity=minimum_velocity,
                                                         maximum_velocity=maximum_velocity
                                                         )
        temp_monitor_filtered.get_location_data()
        temp_monitor_filtered.get_visit_data(begin, end)
        temp_monitor_filtered.node_name = node_name

        if all_filter_dates[location_id] is not None:
            filter_dates = all_filter_dates[location_id]
            beg, end = filter_dates[0]
            temp_monitor_filtered.raw_data = temp_monitor1.raw_data.loc[beg: end].copy()
            for beg, end in filter_dates[1:]:
                print(beg)
                print(end)
                test = temp_monitor1.raw_data.loc[beg: end].copy()
                temp_monitor_filtered.raw_data = temp_monitor_filtered.raw_data.append(test)
            temp_monitor_filtered.process_raw_data()
            temp_monitor_filtered.filter_raw_data(5)

            regular_flow_path_name = "/" + basin_name + "/" + temp_monitor_filtered.node_name + " " + str(location_id) + "/FLOW//5MIN/QAQC/"
            irregular_flow_path_name = "/" + basin_name + "/" + temp_monitor_filtered.node_name + " " + str(location_id) + "/FLOW//IR-DECADE/RAW/"

            # regular_velocity_path_name = "/" + basin_name + "/" + temp_monitor_filtered.node_name + " " + str(location_id) + "/VELOCITY//5MIN/QAQC/"
            # irregular_velocity_path_name = "/" + basin_name + "/" + temp_monitor_filtered.node_name + " " + str(location_id) + "/VELOCITY//IR-DECADE/RAW/"
            #
            # regular_stage_path_name = "/" + basin_name + "/" + temp_monitor_filtered.node_name + " " + str(location_id) + "/STAGE//5MIN/QAQC/"
            # irregular_stage_path_name = "/" + basin_name + "/" + temp_monitor_filtered.node_name + " " + str(location_id) + "/STAGE//IR-DECADE/RAW/"

            data_io.write_5_minute_filtered_flow_to_regular_dss(dss_file_path, regular_flow_path_name,
                                                                temp_monitor_filtered.filtered_flow_data)
            # data_io.write_5_minute_filtered_depth_in_inches_dss(dss_file_path, regular_stage_path_name,
            #                                                     temp_monitor_filtered.filtered_depth_data)
            # data_io.write_5_minute_filtered_velocity_in_feet_per_second_dss(dss_file_path, regular_velocity_path_name,
            #                                                     temp_monitor_filtered.filtered_velocity_data)

            data_io.write_raw_flow_data_to_irregular_dss(dss_file_path, irregular_flow_path_name, temp_monitor_filtered.flow_data.dropna())
            #data_io.write_raw_flow_data_to_irregular_dss(dss_file_path, irregular_flow1_path_name, temp_monitor_filtered.filtered_flow_data.dropna())
            # data_io.write_raw_depth_data_in_inches_to_irregular_dss(dss_file_path, irregular_stage_path_name,
            #                                                       temp_monitor_filtered.depth_data.dropna())

        else:
            print("no dates")

# begin_dates = [datetime(year=2001, month=8, day=3, hour=0, minute=0)]
# end_dates = [datetime(year=2021, month=11, day=28, hour=0, minute=0)]
# basin_names = ["Tryon"]
# location_id = [14211315]
#
# input_data = zip(begin_dates, end_dates, basin_names, location_id)
#
# dss_file_path = r"C:\Temp\Tryon.dss"
#
# minimum_depth = 0
#
# # begin = '2001-08-03'
# # end = '2021-11-28'
#
# data_io = BaseDataIo()
# for begin_date, end_date, basin_name, location_id in input_data:
#     usgs_begin_date = begin_date.strftime("%Y-%m-%d")
#     usgs_end_date = end_date.strftime("%Y-%m-%d")
#     usgs_gage = TemporaryFlowMonitorData(location_id, True, False, True, minimum_depth=minimum_depth)
#     usgs_gage.get_usgs_data(usgs_begin_date, usgs_end_date)
#     usgs_gage.filter_usgs_raw_data(5)
#     regular_flow_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/FLOW//5MIN/FILTER/"
#     irregular_flow_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/FLOW//IR-DECADE/RAW/"
#     regular_stage_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/STAGE//5MIN/FILTER/"
#     irregular_stage_path_name = "/" + basin_name + "/" + "USGS" + str(location_id) + "/STAGE//IR-DECADE/RAW/"
#
#     data_io.write_5_minute_filtered_flow_to_regular_dss(dss_file_path, regular_flow_path_name, usgs_gage.filtered_flow_data)
#     data_io.write_5_minute_filtered_depth_in_feet_dss(dss_file_path, regular_stage_path_name, usgs_gage.filtered_depth_data)
#     data_io.write_raw_flow_data_to_irregular_dss(dss_file_path, irregular_flow_path_name, usgs_gage.flow_data)
#     data_io.write_raw_depth_data_in_feet_to_irregular_dss(dss_file_path, irregular_stage_path_name, usgs_gage.depth_data)

