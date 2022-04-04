from plotting.plot_precipitation import PrecipitationPlot
from plotting.plot_flow import FlowPlot
from plotting.plot_depth import DepthPlot
from plotting.plot_velocity import VelocityPlot
from plotting.plot_flow_scatter import FlowScatterPlot
from plotting.plot_velocity_scatter import VelocityScatterPlot
from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from met_data.businessclasses.precipitation_gage import PrecipitationGage
import matplotlib.pyplot as plt
import matplotlib.dates as dates1
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.style as mplstyle
mplstyle.use('fast')

#                   Saltzmann
#                   6799 AMM001 QAQC

#                   Stephens
#                                   10310 ACS422 Greater Portland Bible Church
#                   6442 ACS400 # This gage tends to over predict volume not sure how to qaqc
#                   4849 ACS613 # QAQC 5/31/2006 - 10/13/2014 Data quality better from WY 2010 onward
#                                   6444 AMX092 # 9/28/2009 - 10/12/2010 This gage has significant depth and velocity issues
#                   6441 ACY343 # QAQC 10/9/2009 - 10/12/2010 noticeable shift in data after 1/1/2010
#                   13706 ACY344 # QAQC 11/27/2019 Flodar
#                                6443 QAQC ACY337 10/5/2009 - 10/12/2010
#                   3472 ACY443 # QAQC 8/28/2002 - 9/20/2004

                    #Tryon
# 9072 ACX033 QAQC                      10370  ACX227 QAQ
#                   10373 ACX451 QAQC
# 13833 ADC952
#                   10372 ACX345 QAQC
#                                    10371  ANL866 QAQC swapped out to flotote 2019-11-14
#                   10357 ADC775 QAQC Early part of record < 12/1/2018 looks like there may be a blockage/roughness change in fall?
# Falling
#               10359 ADD143 10358 QAQC
#                   6790 ADH086
# Arnold Creek      5635 ADK834
#                   4296 ADK773
#                  USGS 14211315

#location_ids = [9072]

# Woods (QA\QC)
#                           10294 Trib
#               10519 ADC182 # issues with depth sensor 2020-01-09 swapped to ultrasonic on 2020-02-25
#location_ids = [10294]

# South Ash (QA/QC)
# 5367 ADJ264 # depth/velocity switched? Changed to ultrasonic depth sensor in March 2019
# 10497 ADF622 # significant difference between submerged depth sensor and u sonic depth sensor installed in March 2019

# Fanno
#                   Council Crest
#                   Ivey
#                   13838 Dosch road
#                   6460 QAQC not sure why this gage backwaters?
#                   Unnamed 2
#                   13837 SW Boundary St
# 1289 wq?
#                   3472 ACY443 # 8/28/2002 - 9/20/2004
# USGS 14206900 1990-10-01 to 2021-06-28  to 2007-10-01 to 2021-06-28

all_filter_dates = {
    # Council Crest (Snow February 11-15 2021 Melt through 20th? )
                13838:
                [('2021-01-26 14:00', '2021-01-30 08:00'),
                 ('2021-01-30 17:00', '2021-02-05 10:00'),
                 ('2021-02-25  9:00', '2021-03-05 00:00'),
                 ('2021-03-05 01:00', '2021-03-17 12:00'),
                 ('2021-03-21', '2021-03-25 10:00'),
                 ('2021-03-28 12:00', '2021-03-31'),
                 ('2021-06-11 06:00', '2021-06-15 16:00'),
                 ('2021-09-17 22:00', '2021-09-20 0:00'),
                 ('2021-09-27 1:00', '2021-10-21'),
                 ('2021-10-21', '2021-11-17'),
                 ('2021-11-17', "2021-12-02 11:00"),
                 ("2021-12-03 00:00", '2022-02-03')], # '2021-06-15 16:00')],
    # ,'2021-10-01')],
    # Council Crest
                13837:
                [('2021-01-21', '2021-02-03 1:15'),
                 ('2021-02-03 1:50', '2021-02-07'),
                 ('2021-02-25 9:00', '2021-04-10 00:00'),
                 ('2021-04-24 0:00', '2021-07-01 00:00'),
                 ('2021-09-01', '2021-10-14'),
                 ('2021-10-14', '2021-10-30 4:00'),
                 ('2021-10-30 7:00', '2021-11-17'),
                 ('2021-11-17', '2022-01-25')],
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
                 ('2014-02-18 12:00', '2015-04-27')],
                 #('2014-03-06', '2015-04-27')],
    # Tryon
                9072:
                [('2017-05-1', '2018-11-21'),
                 ('2019-02-09', '2019-11-21'),
                 ('2019-11-25', '2020-02-02'),
                 ('2020-02-15', '2020-09-22'),
                 ('2020-09-22', '2021-01-12 20:30'),
                 ('2021-01-13 00:30', '2022-01-16')],

                10370: # Removed 9/17 2021 (Data quality poor due to low flows after 2021-6-15)
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
                 ('2021-09-17', '2021-11-15 11:00'),
                 ('2021-11-15 21:00', '2022-1-16')],

                4283:  # BEFORE 2010-11-10 WQ
                [('2010-11-10', '2011-05-06')],

                13833: # Blockage downstream of monitor
                [('2021-01-01', '2021-02-21 10:00'),
                 ('2021-02-22 12:00', '2021-03-10'),
                 ('2021-03-20 13:00', '2021-03-24'),
                 ('2021-03-28 13:00', '2021-03-29'),
                 ('2021-04-24 4:00', '2021-04-24 18:00'),
                 ('2021-09-18 0:00', '2021-09-18 15:00'),
                 ('2021-09-18 23:30', '2021-09-19 3:00'),
                 ('2021-09-19 03:35', '2021-09-19 07:00'),
                 ('2021-09-19 12:40', '2021-09-19 17:00'),
                 ('2021-11-05 00:00', '2021-11-08 12:00'),
                 ('2021-11-08 21:00', '2021-11-22-12:00'),
                 ('2021-11-22 21:00', '2021-12-01 12:00'),
                 ('2021-12-04 14:00', '2021-12-05 0:00'),
                 ('2021-12-06 4:00', '2022-01-16')],

                10372:
                [('2018-05-01', '2019-10-16'),
                 ('2019-10-28', '2019-11-17'),
                 ('2019-11-28', '2019-12-06'),
                 ('2020-01-07', '2020-01-25'),
                 ('2020-02-12', '2020-07-01'),
                 ('2020-07-01', '2020-09-01'),
                 ('2020-09-11', '2021-01-02'),
                 ('2021-01-12 19:00', '2021-04-30'),
                 ('2021-04-30', '2022-01-16')], # 2021-01-04 to 2021-01-11 blockage?

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
                 ('2021-01-22 00:00', '2022-01-16')],
    # Falling
                13823: #Still waiting on 2021-10-11 data could clean up a few things in the earlier data
                [('2020-12-01', '2021-06-15'),
                 ('2021-06-15', '2022-01-16')],

                4282: # doesn't seem to have data WQ?
                [('2005-2-2', '2009-12-16')],

                10359: # blockage after late January event
                [('2007-05-01', '2018-10-20'),
                 ('2018-10-24', '2018-11-10'),
                 ('2018-11-17', '2018-11-18'),
                 ('2018-11-21', '2020-07-01'),
                 ('2020-07-01', '2020-09-22'),
                 ('2020-09-22', '2021-04-30'),
                 ('2021-04-30', '2021-05-06'),
                 ('2021-05-08 6:00', '2021-05-10'),
                 ('2021-05-13', '2021-05-20 00:00'),
                 ('2021-05-22 12:00', '2021-06-26'),
                 ('2021-09-18', '2021-09-18 3:00'),
                 ('2021-09-18 9:00', '2021-10-11 4:00'),
                 ('2021-10-12 18:00', '2021-10-15 0:00'),
                 ('2021-10-17 15:00', '2021-10-18 6:00'),
                 ('2021-10-19 23:00', '2021-10-24 20:00'),
                 ('2021-10-25 12:20', '2021-10-27 0:00'),
                 ('2021-10-28 23:00', '2021-10-30'),
                 ('2021-11-03 19:00', '2021-11-11 22:20'),
                 ('2021-11-11 22:40', '2021-11-29 18:00'),
                 ('2021-12-03 23:00', '2021-12-11 7:00'),
                 ('2021-12-12 16:00', '2022-01-16')],

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
                 ('2021-04-30', '2021-06-21'),
                 ('2021-09-17 22:00', '2022-11-15 1:00'),
                 ('2022-11-15 1:25', '2022-01-16')],  #Flow quality poor from 2021 6 21 to 2021 9 13
                6790: # Maple Crest
                [('2010-10-01', '2011-10-01')],

                1556: # Boones Ferry
                [('1990-10-01', '2011-10-01')],

                4296: # Boones Ferry
                [('2010-10-01', '2011-10-01')],
                1209: # Upper Arnold # Don't know what was collected flow data not available?
                [('1996-10-29', '1998-07-01')],
                5365: # Arnold
                [('2007-04-01', '2011-10-01')],
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

                10294:
                [('2017-10-01', '2018-2-21 10:00'),
                 ('2018-3-14', '2018-4-25'),
                 ('2018-10-5 10:00', '2018-11-3'),
                 ('2018-11-6', '2020-05-26')],
                10427:
                [('2021-01-01', '2022-02-01')],
                10426:
                [('2021-01-01', '2022-02-01')]
    }

location_ids = all_filter_dates.keys()
location_ids = [13838]
# begin = '2009-10-01'
# begin = '2017-05-01'
begin = '2021-01-01'
end = '2022-03-07'
# begin = '2005-2-2'
# end ='2009-12-16'
# begin = '2010-11-10'
# end = '2011-05-06'
# begin = '2007-04-01'
# end = '2008-6-9'
# begin = '1996-10-29'
# end = '1998-07-01'
# begin = '1990-10-01'
# end = '2011-10-01'
# 13837
# begin_swap = '2021-06-08 13:00'
# end_swap = '2021-07-01'
# swap_flow = True
# swap_depth = False


# 5367
# begin_swap = '2021-05-13'
# end_swap = '2021-06-01'
# swap_flow = False
# swap_depth = True


begin_swap = None
end_swap = None

begin_plot = begin
end_plot = end

minimum_depth = 0.7
maximum_depth = 10000
minimum_velocity = 0
maximum_velocity = 10000


# location_id = 14211315
# temp_monitor1 = TemporaryFlowMonitorData(location_id, True, False, True, minimum_depth=minimum_depth)
# temp_monitor1.get_usgs_data(begin, end)
# temp_monitor1.filter_usgs_raw_data(15)


class FigureDataReview(object):
    def __init__(self, begin, end, precipitation_gages, monitor_data_sets):
        self.precipitation_gages = precipitation_gages
        self.monitor_data_sets = monitor_data_sets
        self.flow = monitor_data_sets.flow
        self.velocity = monitor_data_sets.velocity
        self.depth = monitor_data_sets.depth
        self.begin = begin
        self.end = end
        self.fig = None
        self.default_text_fontsize = 'xx-small'
        self.default_label_fontsize = 'x-small'
        self.default_title_fontsize = 'small'
        self.precipitation_plot = None
        self.flow_plot = None
        self.depth_plot = None
        self.velocity_plot = None
        self.flow_scatter_plot = None
        self.velocity_scatter_plot = None
        self.fig = None

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.xlim_beg_orig = None
        self.xlim_end_orig = None
        self.ylim_beg_orig = None
        self.ylim_end_orig = None
        self.timestep_forward = None
        self.timestep_backward = None
        self.timestep_name = None

    def set_figure_format_params(self):
        plt.rcParams['legend.title_fontsize'] = self.default_text_fontsize
        plt.rcParams['legend.fontsize'] = self.default_text_fontsize
        plt.rcParams['axes.labelsize'] = self.default_label_fontsize
        plt.rcParams['axes.titlesize'] = self.default_title_fontsize
        plt.rcParams['figure.titlesize'] = self.default_title_fontsize
        plt.rcParams['xtick.labelsize'] = self.default_text_fontsize
        plt.rcParams['ytick.labelsize'] = self.default_text_fontsize

    def create_figure(self):
        self.set_figure_format_params()
        self.fig = plt.figure(constrained_layout=False)

        gs4 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.60, top=.9, bottom=0.80, hspace=0.0)
        ax_precip = self.fig.add_subplot(gs4[0, 0])

        gs3 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.60, top=0.8, bottom=0.4, hspace=0.0)
        ax_flow = self.fig.add_subplot(gs3[0, 0], sharex=ax_precip)

        gs2 = self.fig.add_gridspec(nrows=2, ncols=1, left=0.1, right=0.60, top=0.4, bottom=0.1, hspace=0.0)
        ax_depth = self.fig.add_subplot(gs2[1, 0], sharex=ax_precip)
        ax_velocity = self.fig.add_subplot(gs2[0, 0], sharex=ax_precip)

        gs1 = self.fig.add_gridspec(nrows=2, ncols=1, left=0.7, right=0.95, top=.9, bottom=0.1, hspace=0.2)
        ax_scatter_flow = self.fig.add_subplot(gs1[0, 0])

        ax_scatter_velocity = self.fig.add_subplot(gs1[1, 0])

        self.precipitation_plot = PrecipitationPlot(self.begin, self.end, precipitation_gages, ax_precip)
        self.precipitation_plot.create_plot()
        if self.flow:
            self.flow_plot = FlowPlot(self.begin, self.end, ax_flow, [self.monitor_data_sets])
            self.flow_plot.create_plot()
        if self.velocity:
            self.velocity_plot = VelocityPlot(self.begin, self.end, ax_velocity, [self.monitor_data_sets])
            self.velocity_plot.create_plot()
        if self.depth:
            self.depth_plot = DepthPlot(self.begin, self.end, ax_depth, [self.monitor_data_sets])
            self.depth_plot.create_plot()
            self.depth_plot.xaxis_visible()

        if self.flow and self.depth:
            self.flow_scatter_plot = FlowScatterPlot(self.begin, self.end, ax_scatter_flow, [self.monitor_data_sets])
            self.flow_scatter_plot.create_plot()
        if self.velocity and self.depth:
            self.velocity_scatter_plot = VelocityScatterPlot(self.begin, self.end, ax_scatter_velocity, [self.monitor_data_sets])
            self.velocity_scatter_plot.create_plot()

        # self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        # self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.precipitation_plot.axs.callbacks.connect('xlim_changed', self.onzoom)
        if self.flow:
            self.flow_plot.axs.callbacks.connect('xlim_changed', self.onzoom)
        if self.depth:
            self.depth_plot.axs.callbacks.connect('xlim_changed', self.onzoom)
        if self.velocity:
            self.velocity_plot.axs.callbacks.connect('xlim_changed', self.onzoom)

        self.fig.autofmt_xdate()
        plt.show()

    def onzoom(self, event):
        a = event.axes

        beg_num, end_num = a.get_xlim()
        beg_date = dates1.num2date(beg_num, tz=None)
        end_date = dates1.num2date(end_num, tz=None)
        beg_date = beg_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=None)
        self.precipitation_plot.peak_and_total_precip.update_anchor_text(beg_date, end_date)
        if self.flow:
            self.flow_plot.peak_flow_and_volume.update_anchor_text(beg_date, end_date)
        if self.depth:
            self.depth_plot.peak_depth.update_anchor_text(beg_date, end_date)
        if self.velocity:
            self.velocity_plot.peak_velocity.update_anchor_text(beg_date, end_date)

        if self.flow and self.depth:
            self.flow_scatter_plot.update_scatter_plot(beg_date, end_date)
        if self.velocity and self.depth:
            self.velocity_scatter_plot.update_scatter_plot(beg_date, end_date)

        self.fig.canvas.draw_idle()

    def onpick(self, event):
        if event.artist is not None:
            if event.artist in self.precipitation_plot.lined.keys():
                self.precipitation_plot.data_set_visibility(event)
            elif event.artist in self.flow_plot.lined.keys():
                self.flow_plot.data_set_visibility(event)
            elif event.artist in self.depth_plot.lined.keys():
                self.depth_plot.data_set_visibility(event)
            elif event.artist in self.velocity_plot.lined.keys():
                self.velocity_plot.data_set_visibility(event)
        self.fig.canvas.draw_idle()

input_wdm = r"V:\HydroModHSPF\Models\HSPFWorkshopMaterials\HSPFData\Met5min.wdm"
rgs = [161, 227, 172]
precipitation_gages = []
for rg in rgs:
    precipitation_gage = PrecipitationGage(rg)
    precipitation_gage.read_raw_data_from_wdm(input_wdm)
    precipitation_gage.read_filled_data_from_wdm(input_wdm)
    precipitation_gages.append(precipitation_gage)

# import matplotlib.pyplot as plt
# temp_monitor1.flow_data.plot()
# plt.show()
#
# temp_monitor1.depth_data.plot()
# plt.show()

# figure_data_review = FigureDataReview(begin, end, precipitation_gages, temp_monitor1)
# figure_data_review.create_figure()

for location_id in location_ids:
    temp_monitor1 = TemporaryFlowMonitorData(location_id, True, True, True, minimum_depth=minimum_depth)
    temp_monitor1.get_raw_data(begin, end)
    if begin_swap is not None and end_swap is not None:
        temp_monitor1.swap_velocity_and_flow(begin_swap, end_swap)
    temp_monitor1.get_location_data()
    node_name = temp_monitor1.location_data['manhole_hansen_id'][0]
    temp_monitor1.get_visit_data(begin, end)
    temp_monitor1.node_name = node_name
    beg_obs = temp_monitor1.raw_data.index.values[0]
    end_obs = temp_monitor1.raw_data.index.values[-1]
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)
    print(temp_monitor1.visit_data)

    temp_monitor_filtered = TemporaryFlowMonitorData(location_id, True, True, True, minimum_depth=minimum_depth,
                                                                                    maximum_depth=maximum_depth,
                                                                                    minimum_velocity=minimum_velocity,
                                                                                    maximum_velocity=maximum_velocity
                                                                                    )

    temp_monitor_filtered.get_location_data()
    temp_monitor_filtered.get_visit_data(begin, end)
    temp_monitor_filtered.node_name = node_name

    #all_filter_dates[location_id] = None

    if all_filter_dates[location_id] is not None:
        filter_dates = all_filter_dates[location_id]
        beg, end = filter_dates[0]
        temp_monitor_filtered.raw_data = temp_monitor1.raw_data.loc[beg: end].copy()
        for beg, end in filter_dates[1:]:
            test = temp_monitor1.raw_data.loc[beg: end].copy()
            temp_monitor_filtered.raw_data = temp_monitor_filtered.raw_data.append(test)
        temp_monitor_filtered.process_raw_data()
        if begin_swap is not None and end_swap is not None:
            if swap_flow:
                temp_monitor_filtered.swap_velocity_and_flow(begin_swap, end_swap)
            if swap_depth:
                temp_monitor_filtered.swap_velocity_and_depth(begin_swap, end_swap)
        temp_monitor_filtered.filter_raw_data(5)
        if begin_swap is not None and end_swap is not None:
            if swap_flow:
                temp_monitor_filtered.swap_filtered_velocity_and_flow(begin_swap, end_swap)
            if swap_depth:
                temp_monitor_filtered.swap_filtered_velocity_and_depth(begin_swap, end_swap)
#        temp_monitor_filtered.filtered_depth_data.to_excel(r"c:\temp\depth.xlsx")
#        temp_monitor_filtered.filtered_flow_data.to_excel(r"c:\temp\flow.xlsx")

        figure_data_review = FigureDataReview(begin_plot, end_plot, precipitation_gages, temp_monitor_filtered)
        figure_data_review.create_figure()
    else:
        temp_monitor1.process_raw_data()
        temp_monitor1.filter_raw_data(5)

        figure_data_review = FigureDataReview(begin, end, precipitation_gages, temp_monitor1)
        figure_data_review.create_figure()


