import metpy
from metpy.io import Level3File
import numpy as np
import pyproj
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.style as mplstyle
import os
from met_data.businessclasses.precipitation_gage import PrecipitationGage
from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from plotting.plot_precipitation import PrecipitationPlot
from plotting.plot_flow import FlowPlot
import pandas as pd
mpl.use('Agg')
mplstyle.use('fast')
from datetime import datetime
from datetime import timedelta
import sys


def instantaneous_rainfall_rate_plot(pp, radar_file, begin, end, current_date,
                                     lon_min, lat_min, lon_max, lat_max,
                                     title, min_rainfall_rate=0.0, max_flow=None,
                                     subbasins=None, rain_gages=None,
                                     precipitation_gages=None,
                                     flow_gages=None):
    #P183 Digital Precipitation Rate DPR
    try:
        if radar_file is not None:
            # Open radar file and extract the data array.
            f = (radar_file if type(radar_file) == metpy.io.Level3File else
                 metpy.io.Level3File(radar_file))

            datadict = f.sym_block[0][0]['components'][4]

            data_list = []
            azmuth_list = []
            for radial_data in datadict:
                data_list.append(radial_data[5])
                azmuth_list.append(radial_data[0])
            data = np.asarray(data_list)/10.0

            with np.errstate(invalid='ignore'):  # ignore existing NaNs
                data[data < min_rainfall_rate] = np.nan  # mask out low values

            azimuth = np.array(azmuth_list + [azmuth_list[-1]])

            distance = np.linspace(0, f.max_range * 1000, data.shape[-1] + 1)

            # Project to EPSG3857 (i.e. "Web Mercator") X and Y coordinates.
            lon, lat, _ = pyproj.Geod(ellps='WGS84').fwd(
                *np.broadcast_arrays(f.lon, f.lat, azimuth[:, None], distance))
            radar_x, radar_y = pyproj.Proj(3857)(lon, lat)

        # Project and verify the bounds for the output image.
        xmin, ymin = pyproj.Proj(3857)(lon_min, lat_min)
        xmax, ymax = pyproj.Proj(3857)(lon_max, lat_max)

        x_delta = xmax - xmin
        y_delta = ymax - ymin

        aspect_ratio = x_delta/y_delta
        aspect_ratio_of_plot_window = 1.5
        aspect_ratio_diff = (aspect_ratio_of_plot_window - aspect_ratio)/2
        if aspect_ratio == aspect_ratio_of_plot_window:
            pass
        elif aspect_ratio < aspect_ratio_of_plot_window:
            # increase x delta
            xmin = xmin - x_delta * aspect_ratio_diff
            xmax = xmax + x_delta * aspect_ratio_diff
        else:
            ymin = ymin - y_delta * aspect_ratio_diff
            ymax = ymax + y_delta * aspect_ratio_diff

        # assert abs(y_res * (xmax - xmin) / (ymax - ymin) - x_res) < 1
        # assert abs(x_res * (ymax - ymin) / (xmax - xmin) - y_res) < 1

        # Generate the output plot.
        plt.rcParams['legend.title_fontsize'] = 'xx-small'
        plt.rcParams['legend.fontsize'] = 'xx-small'
        plt.rcParams['axes.labelsize'] = 'xx-small'
        plt.rcParams['axes.titlesize'] = 'xx-small'
        plt.rcParams['figure.titlesize'] = 'small'
        plt.rcParams['xtick.labelsize'] = 'xx-small'
        plt.rcParams['ytick.labelsize'] = 'xx-small'
        plt.rcParams['figure.dpi'] = 60

        fig = plt.figure(constrained_layout=False)
        fig.suptitle(title)
        gs2 = fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.90, top=0.9, bottom=0.325, hspace=0.0)
        ax_nexrad = fig.add_subplot(gs2[0, 0])

        gs4 = fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.90, top=0.3, bottom=0.20, hspace=0.0)
        ax_precip = fig.add_subplot(gs4[0, 0])

        gs3 = fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.90, top=0.2, bottom=0.10, hspace=0.0)
        ax_flow = fig.add_subplot(gs3[0, 0], sharex=ax_precip)

        precipitation_plot = PrecipitationPlot(begin, end, precipitation_gages, ax_precip)
        precipitation_plot.create_plot()
        precipitation_plot.yaxis_autoscale_on()
        prec_ymax, prec_ymin = ax_precip.get_ylim()
        ax_precip.set_ylim(prec_ymax, 0)

        flow_plot = FlowPlot(begin, end, ax_flow, flow_gages)
        flow_plot.create_plot()
        flow_plot.xaxis_visible()

        if current_date is not None:
            ax_flow.scatter([current_date], [0])
        if max_flow is not None:
            ax_flow.set_ylim(0, max_flow)
#       flow_plot.yaxis_autoscale_on()

        ax_nexrad.set_xlim(xmin, xmax)
        ax_nexrad.set_ylim(ymin, ymax)
        ax_nexrad.set_axis_off()
        if radar_file is not None:
            cmap = plt.colormaps['RdYlGn_r']
            levels = np.asarray([0.1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 125, 150, 175, 200, 225, 250, 275, 300])
            color_bar_labels = levels / 100.0
            norm = mpl.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)

            plot = ax_nexrad.pcolormesh(radar_x, radar_y, data, norm=norm, cmap=cmap, rasterized=True)

            cbar = fig.colorbar(plot, location='right', ax=ax_nexrad)
            cbar.ax.set_yticklabels(color_bar_labels)

        if subbasins is not None:
            subbasins.boundary.plot(ax=ax_nexrad)
        if rain_gages is not None:
            rain_gages.plot(ax=ax_nexrad)

        if pp is not None:
            pp.savefig()
            plt.clf()
            plt.close(fig)
        else:
            plt.show()
    except:
        plt.clf()
        plt.close(fig)
        print("Plot Failed!")
########################################################################################################################

mpl.pyplot.ioff()
input_file_path = r"C:\Users\sggho\Desktop\NexRAD\CC\HSPFSWMMInputAllSoilsTryon.xlsx"
events = pd.read_excel(input_file_path, sheet_name='Events', header=1)

events = events[events.iloc[:, 2] == 'YES']
print(events.iloc[:, 0:2])
for event in events.itertuples():
    begin_date = event.StartDate #datetime(2014, 3, 28, hour=12)
    stop_date = event.EndDate #datetime(2014, 3, 29, hour=4)

    # begin_date = datetime(2010, 12, 9, hour=15)
    # stop_date = datetime(2010, 12, 9, hour=23)

    # subbasins_input_gdb_folder_path = r"C:\Users\sggho\Documents\HSPFModels\Models\Saltzman_Updated"
    # temporary_flow_monitor_location_id = 6799
    # rain_gage_h2_numbers = [160, 193, 121]
    # model_name = "Saltzman"

    subbasins_input_gdb_folder_path = r"C:\Users\sggho\Documents\HSPFModels\Models\CCStorm_detailed_model_all_soils_existing_ii"
    temporary_flow_monitor_location_id = 13837
    rain_gage_h2_numbers = [161, 227]
    model_name = "CC"

    hours_from_utc = 8
    bounds_buffer_percentage = 50


    bounds_buffer = bounds_buffer_percentage/100

    #file paths
    output_pdf_file_path = r"C:\Users\sggho\Desktop\NexRAD\\CC\\" + model_name + begin_date.strftime("%Y%m%d") + ".pdf"
    subbasins_layer = "areas"
    subbasins_input_gdb = "EmgaatsModel.gdb"
    subbasins_input_gdb_file_path = subbasins_input_gdb_folder_path + "\\" + subbasins_input_gdb

    rain_gage_layer = "raingages"
    rain_gage_input_gdb = "raingages.gdb"
    rain_gage_input_gdb_folder_path = r"C:\Users\sggho\Desktop\NexRAD"
    rain_gage_input_gdb_file_path = rain_gage_input_gdb_folder_path + "\\" + rain_gage_input_gdb

    met_data_wdm_file_path = r"C:\Users\sggho\Documents\HSPFModels\HSPFWorkshopMaterials\HSPFData\Met5min.wdm"

    temporary_flow_monitor_data_folder_path = r"C:\Users\sggho\Documents\HSPFModels\HSPFWorkshopMaterials\HSPFData\ObservedFlow"
    temporary_flow_monitor_data_raw_data_path = temporary_flow_monitor_data_folder_path + "\\" +\
                                            "raw" + str(temporary_flow_monitor_location_id) + ".h5"
    temporary_flow_monitor_data_filtered_data_path = temporary_flow_monitor_data_folder_path + "\\" +\
                                                 "filtered" + str(temporary_flow_monitor_location_id) + ".h5"

    nexrad_data_folder_path = r"C:\Users\sggho\Desktop\NexRAD_raw\workingDPR"

    nexrad_keyword = "DPR"

    # load geometry
    subbasins = gpd.read_file(subbasins_input_gdb_file_path, layer=subbasins_layer)
    subbasins_web_mercator = subbasins.to_crs(epsg="3857")
    subbasins_wgs = subbasins.to_crs("WGS84")

    # get bounds
    rain_gages = gpd.read_file(rain_gage_input_gdb_file_path, layer=rain_gage_layer)
    rain_gages = rain_gages[rain_gages["h2_number"].isin(rain_gage_h2_numbers)]
    rain_gages_web_mercator = rain_gages.to_crs(epsg="3857")
    rain_gages_wgs = rain_gages.to_crs("WGS84")

    subbasins_x_min, subbasins_y_min, subbasins_x_max, subbasins_y_max = subbasins.total_bounds
    rain_gage_x_min, rain_gage_y_min, rain_gage_x_max, rain_gage_y_max = rain_gages.total_bounds

    subbasins_lon_min, subbasins_lat_min, subbasins_lon_max, subbasins_lat_max = subbasins_wgs.total_bounds
    rain_gage_lon_min, rain_gage_lat_min, rain_gage_lon_max, rain_gage_lat_max = rain_gages_wgs.total_bounds

    x_delta = rain_gage_x_max - rain_gage_x_min
    y_delta = rain_gage_y_max - rain_gage_y_min
    x_min = rain_gage_x_min - bounds_buffer * x_delta
    y_min = rain_gage_y_min - bounds_buffer * y_delta
    x_max = rain_gage_x_max + bounds_buffer * x_delta
    y_max = rain_gage_y_max + bounds_buffer * y_delta

    lon_delta = rain_gage_lon_max - rain_gage_lon_min
    lat_delta = rain_gage_lat_max - rain_gage_lat_min
    lon_min = rain_gage_lon_min - bounds_buffer * lon_delta
    lat_min = rain_gage_lat_min - bounds_buffer * lat_delta
    lon_max = rain_gage_lon_max + bounds_buffer * lon_delta
    lat_max = rain_gage_lat_max + bounds_buffer * lat_delta

    # get rain gages
    precipitation_gages = []
    for rain_gage_h2_number in rain_gage_h2_numbers:
        precipitation_gage = PrecipitationGage(rain_gage_h2_number)
        precipitation_gage.read_filled_data_from_wdm(met_data_wdm_file_path)
        precipitation_gages.append(precipitation_gage)

    # get flow data
    temporary_flow_monitors = []
    temporary_flow_monitor = TemporaryFlowMonitorData(location_id=temporary_flow_monitor_location_id, flow=True)
    temporary_flow_monitor.get_filtered_flow_data_from_hdf5(temporary_flow_monitor_data_filtered_data_path)
    temporary_flow_monitor.get_flow_data_from_hdf5(temporary_flow_monitor_data_raw_data_path)
    temporary_flow_monitor.node_name = ""
    temporary_flow_monitor.filtered_time_step = 5
    temporary_flow_monitors.append(temporary_flow_monitor)

    max_flow = 0
    max_filtered_flow = temporary_flow_monitor.filtered_flow_data.loc[begin_date: stop_date].max()[0]
    max_raw_flow = temporary_flow_monitor.flow_data[~temporary_flow_monitor.flow_data.index.duplicated(keep='first')].loc[begin_date: stop_date].max()[0]
    if max_filtered_flow >= max_raw_flow:
        max_flow = max_filtered_flow - max_filtered_flow % 1 + 1
    else:
        maxflow = max_raw_flow - max_raw_flow % 1 + 1

    # begin end integer time stamps in UTC
    timestamp_string_format = "%Y%m%d%H%M"
    begin_date_utc = begin_date + timedelta(hours=hours_from_utc)
    stop_date_utc = stop_date + timedelta(hours=hours_from_utc)
    begin_date_utc_integer_date_stamp = int(begin_date_utc.strftime(timestamp_string_format))
    stop_date_utc_integer_date_stamp = int(stop_date_utc.strftime(timestamp_string_format))

    pp = PdfPages(output_pdf_file_path)
    Nexrad = False
    with os.scandir(nexrad_data_folder_path) as dirs:
        for entry in dirs:
            nexrad_file_name = str(entry.name)
            nexrad_file_path = str(entry.path)
            nexrad_date_string = nexrad_file_name[-12: len(nexrad_file_name)]
            integer_nexrad_date_stamp = int(nexrad_date_string)
            if begin_date_utc_integer_date_stamp <= integer_nexrad_date_stamp and \
                stop_date_utc_integer_date_stamp >= integer_nexrad_date_stamp:
                Nexrad = True
                print(str(integer_nexrad_date_stamp))

                radar_file = Level3File(nexrad_file_path)
                current_date_utc = datetime.strptime(nexrad_date_string, timestamp_string_format)
                current_date_pac = current_date_utc - timedelta(hours=hours_from_utc)
                title = current_date_pac.strftime("%Y%m%d %H:%M")
                instantaneous_rainfall_rate_plot(pp, radar_file, begin_date, stop_date, current_date_pac,
                                                 lon_min, lat_min, lon_max, lat_max,
                                                 title, min_rainfall_rate=0.001, max_flow=max_flow,
                                                 subbasins=subbasins_web_mercator, rain_gages=rain_gages_web_mercator,
                                                 precipitation_gages=precipitation_gages, flow_gages=temporary_flow_monitors)
        if not Nexrad:
            title = "No Nexrad"
            instantaneous_rainfall_rate_plot(pp, None, begin_date, stop_date, None,
                                             lon_min, lat_min, lon_max, lat_max,
                                             title, min_rainfall_rate=0.001, max_flow=max_flow,
                                             subbasins=subbasins_web_mercator, rain_gages=rain_gages_web_mercator,
                                             precipitation_gages=precipitation_gages,
                                             flow_gages=temporary_flow_monitors)
    pp.close()
    print("***")
