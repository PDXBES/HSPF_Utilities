from hspf.businessclasses.hspf import Hspf
from hspf.dataio.hspf_dataio import HspfDataIo
from flow_data.businessclasses.simulated_data import SimulatedData
from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from plotting.figure_calibration_data import CalibrationDataReview
from plotting.figure_calibration_peak_flow_data import CalibrationPeakFlowDataReview
from plotting.figure_calibration_total_volume_bar_chart import TotalVolumeFlowBarChart
from met_data.businessclasses.precipitation_gage import PrecipitationGage

import pandas as pd
from common.simpleprogressbar import SimpleProgressBar
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.style as mplstyle
mplstyle.use('fast')
from PyQt5.QtWidgets import QApplication
from common.file_dialog import App
import sys
import math
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

print("#######################################################################")
print("# The program has started. A file dialog box should appear shortly    #")
print("# in order to allow you to select an hspf swmm input excel file       #")
print("# to start a simulation.                                              #")
print("#######################################################################")

app = QApplication(sys.argv)
ex = App()
input_file = ex.fileName

print("Running: " + input_file)

total_progressbar = SimpleProgressBar()
if not input_file == '':
    hspf_data_io = HspfDataIo(input_file)
    hspf = Hspf(hspf_data_io)
else:
    print("No file Selected.")
    sys.exit()

start_date_hru, start_date_swmm, start_date_lumped, plot_start_date, \
stop_date_hru, stop_date_swmm, stop_date_lumped, plot_stop_date = \
    hspf_data_io.read_simulation_start_and_stop_dates()

run_lumped, run_hspf_swmm, run_hspf_hru, post_process_lump, post_process_swmm = hspf_data_io.read_simulation_and_post_processing()

hspf.perlnds = hspf.create_perlnds(hspf_data_io.read_hspf_input_file_perlnds())
hspf.implnds = hspf.create_implnds(hspf_data_io.read_hspf_input_file_implnds())

hspf.start_date_time = start_date_swmm
hspf.stop_date_time = stop_date_swmm

swmm_start_date = start_date_swmm.strftime("%m/%d/%Y")
swmm_stop_date = stop_date_swmm.strftime("%m/%d/%Y")
hspf_start_date_hru = start_date_hru.strftime("%Y %m %d")
hspf_stop_date_hru = stop_date_hru.strftime("%Y %m %d")
hspf_start_date_lumped = start_date_lumped.strftime("%Y %m %d")
hspf_stop_date_lumped = stop_date_lumped.strftime("%Y %m %d")

#saltzman_precip_gage_h2_numbers_for_plots = [121, 160, 192, 193]

events = hspf_data_io.read_events()
emgaats_model_folder, win_hspf_lt_path, swmm_exe_path, observed_data_folder = hspf_data_io.read_file_paths()
gage_location_id, swmm_link, lumped_model_rchres, locations_title_for_plots = hspf_data_io.read_observed_and_simulation_data()
name, description = hspf_data_io.read_simulation_name_and_description()
rain_gage, rain_gage_multiplier, pan_evap_evapotranspiration = hspf_data_io.read_precip_and_evap()

run_overlay = False
run_hru = False
run_import_transects = False
run_import_losses = False
run_swmm = False
run_hspf_lumped = False
run_post_processing = True


rgs = [rain_gage]
if run_post_processing:
    if len(swmm_link) > 1:
        simulated_link_names = swmm_link
        monitor_location_ids = gage_location_id
        plot_title = locations_title_for_plots
    else:
        simulated_link_names = [swmm_link.values[0]]
        monitor_location_ids = [gage_location_id.values[0]]
        plot_title = [locations_title_for_plots.values[0]]

precipitation_gage_h2_numbers_for_plots = [227, 161, 172]

# TODO need to update reporting block in swmm inp

for rg in rgs:
    emgaats_simulation_folder = emgaats_model_folder + "\\" + "sim"
    hspf_input_file_path = observed_data_folder
    observed_flow_file_path = observed_data_folder + "\\" + "ObservedFlow"
    swmm_simulation_file_path = emgaats_simulation_folder + "\\" + name + "_RG" + str(rg)
    hspf_simulation_file_path = swmm_simulation_file_path

    path_to_swmm_executable = swmm_exe_path
    path_to_hspf_executable = win_hspf_lt_path
    path_to_input_met_wdm_file = hspf_input_file_path
    path_to_input_uci_file = hspf_input_file_path


    name_of_input_met_wdm = "Met5min.wdm"
    name_of_swmm_inp_file = "SWMM.inp"
    name_of_swmm_out_file = "SWMM.out"
    name_of_swmm_rpt_file = "SWMM.rpt"

    input_met_wdm_file_path = path_to_input_met_wdm_file + "\\" + name_of_input_met_wdm

    simulation_input_met_wdm_file_path = hspf_simulation_file_path + "\\" + name_of_input_met_wdm
    simulation_swmm_inp_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_inp_file
    simulation_swmm_out_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_out_file
    simulation_swmm_rpt_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_rpt_file

    if run_post_processing:
        print("Running HSPF/SWMM model post processing")
        precipitation_gages = []
        simulated_data_sets = []
        observed_data_sets = []
        print("Getting observed and simulated data")

        for simulated_link_name in simulated_link_names:
            simulated_data = SimulatedData(link_name=simulated_link_name)
            simulated_data.get_sim_flow_data(simulation_swmm_out_file_path)
            simulated_data.filtered_time_step = 5 #TODO get timestep
            simulated_data_sets.append(simulated_data)

        print("Temporary monitor data")
        for monitor_location in monitor_location_ids:
            filtered_monitor_file = observed_flow_file_path + "\\" + "filtered" + str(monitor_location) + ".h5"
            monitor_file = observed_flow_file_path + "\\" + "raw" + str(monitor_location) + ".h5"
            temporary_flow_monitor = TemporaryFlowMonitorData(monitor_location, flow=True)
            temporary_flow_monitor.get_filtered_flow_data_from_hdf5(filtered_monitor_file)
            temporary_flow_monitor.get_flow_data_from_hdf5(monitor_file)
            temporary_flow_monitor.node_name = str(monitor_location)
            temporary_flow_monitor.filtered_time_step = 5 #TODO get timestep
            observed_data_sets.append(temporary_flow_monitor)

        print("Filter Simulated data")
        for index, simulated_link_name in enumerate(simulated_link_names):
            simulated_data = simulated_data_sets[index].flow_data
            observed_data = observed_data_sets[index].filtered_flow_data
            long_term_statistics = simulated_data_sets[index].filter_data_based_on_data_from_another_source(simulated_data, observed_data)
            simulated_data_sets[index].filtered_flow_data = long_term_statistics  # TODO clean this up

        print("Precipitation data")
        for gage in precipitation_gage_h2_numbers_for_plots:
            precipitation_gage = PrecipitationGage(gage)
            precipitation_gage.read_raw_data_from_wdm(input_met_wdm_file_path)
            precipitation_gage.read_filled_data_from_wdm(input_met_wdm_file_path)
            precipitation_gages.append(precipitation_gage)

        if not events.empty:
            #print("Plotting entire plotting period (This will take a few minutes)")
            pp = PdfPages(swmm_simulation_file_path + "\\" + name + "_RG" + str(rg) + '_events_plots_usgs.pdf')
            file_path = swmm_simulation_file_path + "\\" + name + "_" + str(rg) + "_" + "long_term_and_events_usgs.xlsx"

            with pd.ExcelWriter(file_path) as writer:
                monitor_location_index = -1
                for simulated_data_set, observed_data_set in zip(simulated_data_sets, observed_data_sets):
                    monitor_location_index += 1
                    monitor_location = observed_data_set.location_id
                    link_name = simulated_data_set.link_name
                    print("Link_name:" + link_name)
                    event_dicts = []
                    events_statistics_list = []
                    for index, event in events.iterrows():
                        if event[monitor_location] == "YES":
                            print("Calculating statistics for event:" + str(event.StartDate))
                            event_start_date = event.StartDate
                            event_stop_date = event.EndDate
                            simulated_peak_flow = simulated_data_set.peak_filtered_flow(event_start_date, event_stop_date)
                            observed_peak_flow = observed_data_set.peak_filtered_flow(event_start_date, event_stop_date)
                            simulated_volume = simulated_data_set.filtered_volume(event_start_date, event_stop_date)
                            observed_volume = observed_data_set.filtered_volume(event_start_date, event_stop_date)
                            try:
                                percent_difference_flow = round((simulated_peak_flow - observed_peak_flow)/observed_peak_flow * 100, 1)
                                percent_difference_volume = round((simulated_volume - observed_volume)/observed_volume * 100, 1)
                            except:
                                percent_difference_flow = None
                                percent_difference_volume = None
                            event_dict = {"Start_Date": event_start_date.strftime("%m/%d/%Y"),
                                          "Stop_Date": event_stop_date.strftime("%m/%d/%Y"),
                                          "Sim_Peak_Flow": simulated_peak_flow,
                                          "Obs_Peak_Flow": observed_peak_flow,
                                          "% Diff_Flow": percent_difference_flow,
                                          "Sim_Volume": simulated_volume,
                                          "Obs_Volume": observed_volume,
                                          "% Diff_Volume": percent_difference_volume}
                            event_dicts.append(event_dict)
                    events_statistics = pd.DataFrame(event_dicts)
                    events_statistics = events_statistics.set_index(events_statistics.index.rename('Events'))
                    events_statistics.dropna()

                    print("writing long term and event statistics")
                    simulated_data = simulated_data_sets[monitor_location_index].flow_data
                    simulated_data = simulated_data.rename(columns={simulated_data.columns[0]: "Sim flow"})
                    observed_data = observed_data_sets[monitor_location_index].filtered_flow_data
                    observed_data = observed_data.rename(columns={observed_data.columns[0]: "Obs flow"})
                    long_term_statistics = simulated_data_sets[monitor_location_index].flow_data

                    simulated = long_term_statistics.copy(deep=True)
                    long_term_statistics = simulated_data_sets[monitor_location_index].filter_data_based_on_data_from_another_source(simulated_data, observed_data)

                    simulated_data_sets[monitor_location_index].filtered_flow_data = long_term_statistics  # TODO clean this up
                    long_term_statistics = long_term_statistics.join(observed_data)
                    obs = long_term_statistics.copy(deep=True)

                    flow = obs.copy(deep=True)
                    #flow = flow.mean().T
                    flow = flow.sum().T
                    flow['% Diff'] = (flow[0] - flow[1])/flow[1] * 100
                    flow.to_excel(writer, sheet_name='Total_Vol_' + link_name, float_format="%0.2f", header=False)
                    total_vol_bar_chart_plot = TotalVolumeFlowBarChart([flow["Obs flow"]],
                                                                     [flow["Sim flow"]],
                                                                     ["Total Volume"],
                                                                     title="Total Volume\n" + plot_title[monitor_location_index]
                                                                     )
                    total_vol_bar_chart_plot.create_figure()
                    total_vol_bar_chart_plot.write_to_pdf(pp)
                    total_vol_bar_chart_plot.close()

                    long_term_statistics = simulated_data_sets[
                        monitor_location_index].compare_total_volume_data_per_water_year(simulated_data, observed_data)
                    if long_term_statistics is not None:
                        wy = long_term_statistics.copy(deep=True)
                        wy['% Diff'] = (wy[wy.columns[0]] - wy[wy.columns[1]])/wy[wy.columns[1]] * 100
                        wy.to_excel(writer, sheet_name='Avg_WY_Vol_' + link_name, float_format="%0.2f")
                        wy_flow_bar_chart_plot = TotalVolumeFlowBarChart(wy["Obs flow"].values,
                                                                            wy["Sim flow"].values,
                                                                            wy.index.values,
                                                                            title="WY Volume\n" + plot_title[monitor_location_index]
                                                                            )
                        wy_flow_bar_chart_plot.create_figure()
                        wy_flow_bar_chart_plot.write_to_pdf(pp)
                        wy_flow_bar_chart_plot.close()

                    long_term_statistics = simulated_data_sets[monitor_location_index].compare_total_volume_data_per_month(
                        simulated_data, observed_data)
                    monthly_avg = long_term_statistics.copy(deep=True)

                    monthly_avg['% Diff'] = (monthly_avg[monthly_avg.columns[0]] - monthly_avg[monthly_avg.columns[1]])/monthly_avg[monthly_avg.columns[1]] * 100

                    monthly = monthly_avg.copy(deep=True)
                    if not obs.empty:
                        monthly = obs.groupby([obs.index.month]).mean()
                        monthly['% Diff'] = (monthly[monthly.columns[0]] - monthly[monthly.columns[1]])/monthly[monthly.columns[1]] * 100
                        monthly.index.name = "Month"
                        monthly.to_excel(writer, sheet_name='Avg_Mon_Vol_' + link_name, float_format="%0.2f")
                        monthly_avg.to_excel(writer, sheet_name='Avg_Mon_Vol_By_Yr_' + link_name, float_format="%0.2f")
                        monthly_avg_vol_bar_chart_plot = TotalVolumeFlowBarChart(monthly["Obs flow"].values,
                                                                                 monthly["Sim flow"].values,
                                                                                 monthly.index.values,
                                                                                 title="Total Monthly Volume\n" + plot_title[
                                                                                     monitor_location_index]
                                                                                 )
                        monthly_avg_vol_bar_chart_plot.create_figure()
                        monthly_avg_vol_bar_chart_plot.write_to_pdf(pp)
                        monthly_avg_vol_bar_chart_plot.close()
                        monthly_flow_bar_chart_plot = TotalVolumeFlowBarChart(monthly_avg["Obs flow"].values,
                                                                                 monthly_avg["Sim flow"].values,
                                                                                 monthly_avg.index.strftime(
                                                                                     "%m-%y").values,
                                                                                 title=plot_title[
                                                                                     monitor_location_index]
                                                                                 )
                        monthly_flow_bar_chart_plot.create_figure()
                        monthly_flow_bar_chart_plot.write_to_pdf(pp)
                        monthly_flow_bar_chart_plot.close()

                    long_term_statistics = simulated_data_sets[monitor_location_index].compare_avg_data_per_day(simulated_data, observed_data)
                    # long_term_statistics.to_excel(writer, sheet_name='Daily_AVG_FLOWS' + simulated_link_name)

                    events_statistics.to_excel(writer, sheet_name='Events_' + link_name, float_format="%0.1f")
                    try:
                        obs.to_excel(writer, sheet_name="SimulatedAndObs_" + link_name)
                        simulated.to_excel(writer, sheet_name="Simulated_" + link_name, float_format="%0.15f")
                    except:
                        print("Could not write 5 min flows to excel.")
                    if not events_statistics.empty:
                        peak_flow_scatter_plot = CalibrationPeakFlowDataReview(events_statistics["Obs_Peak_Flow"].values,
                                                                               events_statistics["Sim_Peak_Flow"].values,
                                                                               events_statistics["Obs_Volume"].values,
                                                                               events_statistics["Sim_Volume"].values,
                                                                               title=plot_title[monitor_location_index])
                        peak_flow_scatter_plot.create_figure()
                        peak_flow_scatter_plot.write_to_pdf(pp)
                        peak_flow_scatter_plot.close()

                event_rain_dicts = []
                for index, event in events.iterrows():
                    start_date = event.StartDate
                    end_date = event.EndDate
                    event_rain_dict = {"Start_Date": start_date.strftime("%m/%d/%Y"),
                                       "Stop_Date": end_date.strftime("%m/%d/%Y")}
                    for precipitation_gage in precipitation_gages:
                        peak_precipitation = precipitation_gage.peak_precipitation(event.StartDate, event.EndDate)
                        event_rain_dict[str(precipitation_gage.h2_number) + "_peak"] = peak_precipitation
                    for precipitation_gage in precipitation_gages:
                        total_precipitation = precipitation_gage.total_precipitation(event.StartDate, event.EndDate)
                        event_rain_dict[str(precipitation_gage.h2_number) + "_tot"] = total_precipitation
                    event_rain_dicts.append(event_rain_dict)
                rain_df = pd.DataFrame(event_rain_dicts)
                rain_df.to_excel(writer, sheet_name='Event_Precip' + link_name, float_format="%0.2f", header=True)


            for index, event in events.iterrows():
                print("Plotting event:" + str(event.StartDate))
                for precipitation_gage in precipitation_gages:
                    precipitation_gage.peak_precipitation(event.StartDate, event.EndDate)
                    precipitation_gage.total_precipitation(event.StartDate, event.EndDate)
                for index, simulated_data in enumerate(simulated_data_sets):
                    if event[observed_data_sets[index].location_id] == "YES":
                        observed_data_sets_1 = [observed_data_sets[index]]
                        simulated_data_sets_1 = [simulated_data]
                        event_start_date = event.StartDate
                        event_stop_date = event.EndDate
                        simulated_peak_flow = simulated_data_sets_1[0].peak_filtered_flow(event_start_date, event_stop_date)
                        observed_peak_flow = observed_data_sets_1[0].peak_filtered_flow(event_start_date, event_stop_date)
                        if simulated_peak_flow > observed_peak_flow:
                            max_flow = simulated_peak_flow
                        else:
                            max_flow = observed_peak_flow

                        if max_flow > 10:
                            max_flow = math.ceil(max_flow / 10) * 10
                        else:
                            max_flow = math.ceil(max_flow)

                        figure_data_review = CalibrationDataReview(event_start_date, event_stop_date,
                                                                   precipitation_gages, observed_data_sets_1,
                                                                   simulated_data_sets_1, title=plot_title[index],
                                                                   peak_flow=max_flow)
                        figure_data_review.create_figure()
                        figure_data_review.write_to_pdf(pp)
                        figure_data_review.close()
            pp.close()

sys.exit()
