from hspf.businessclasses.hspf import Hspf
from hspf.dataio.hspf_dataio import HspfDataIo
from flow_data.businessclasses.simulated_data import SimulatedData
from flow_data.businessclasses.temporary_flow_monitor_data import TemporaryFlowMonitorData
from plotting.figure_calibration_data import CalibrationDataReview
from plotting.figure_calibration_peak_flow_data import CalibrationPeakFlowDataReview
from plotting.figure_calibration_total_volume_bar_chart import TotalVolumeFlowBarChart
from met_data.businessclasses.precipitation_gage import PrecipitationGage
from swmm.transects.swmm_transects_main import main as TransectsMain
from swmm.losses.swmm_losses_main import main as LossesMain
from scipy import stats
from swmmtoolbox import swmmtoolbox
from flow_data.dataio.base_data_io import BaseDataIo
import os

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
import copy
warnings.simplefilter(action='ignore', category=FutureWarning)
import traceback

print("#######################################################################")
print("# The program has started. A file dialog box should appear shortly    #")
print("# in order to allow you to select an hspf swmm input excel file       #")
print("# to start a simulation.                                              #")
print("#######################################################################")

app = QApplication(sys.argv)
ex = App()
input_file = ex.fileName

include_impervious = True
print("Running: " + input_file)

total_progressbar = SimpleProgressBar()
if not input_file == '':
    hspf_data_io = HspfDataIo(input_file)
    hspf = Hspf(hspf_data_io)
else:
    print("No file Selected.")
    sys.exit()

run_obs_to_dss = True

start_date_hru, start_date_swmm, start_date_lumped, \
stop_date_hru, stop_date_swmm, stop_date_lumped = \
    hspf_data_io.read_simulation_start_and_stop_dates()

run_lumped, run_hspf_swmm, run_hspf_hru, post_process_lump, post_process_swmm,\
    include_all_links, write_swmm_to_dss, routing_time_step = hspf_data_io.read_simulation_and_post_processing()

scenario = hspf_data_io.read_scenario()

if scenario == "EXISTING":
    predeveloped = False
elif scenario == "PREDEVELOPED":
    predeveloped = True
elif scenario == "FUTURE":
    predeveloped = False
else:
    print("Unknown Scenario")
    exit()
print("Scenario:" + scenario)


if include_all_links == "YES":
    all_links_in_swmm_output_file = True
else:
    all_links_in_swmm_output_file = False

routing_time_step_in_seconds = int(routing_time_step)

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

events = hspf_data_io.read_events()
emgaats_model_folder, win_hspf_lt_path, swmm_exe_path, observed_data_folder = hspf_data_io.read_file_paths()
gage_location_id, swmm_link, lumped_model_rchres, locations_title_for_plots = hspf_data_io.read_observed_and_simulation_data()
name, description = hspf_data_io.read_simulation_name_and_description()
rain_gage, rain_gage_multiplier, pan_evap_evapotranspiration = hspf_data_io.read_precip_and_evap()

print("Name: " + name)

interactive = False
if not interactive:
    import matplotlib.pyplot as plt
    plt.ioff()

write_swmm_to_dss = "YES"

run_swmm_to_dss = True
run_overlay = False
run_hru = False
run_import_transects = False
run_import_losses = False
run_swmm = False
run_hspf_lumped = False

if run_hspf_hru == "YES":
    run_overlay = False
    run_hru = True
    run_import_transects = False
    run_import_losses = False
    run_swmm = False
    run_hspf_lumped = False

if run_hspf_swmm == "YES" and run_lumped == "YES":
    run_overlay = True
    run_hru = True
    run_import_transects = True
    run_import_losses = True
    run_swmm = True
    run_hspf_lumped = True

elif run_hspf_swmm == "YES":
    run_overlay = True
    run_hru = True
    run_import_transects = True
    run_import_losses = True
    run_swmm = True
    run_hspf_lumped = False

elif run_lumped == "YES":
    run_overlay = False
    run_hru = False
    run_swmm = False
    run_post_processing = False
    run_hspf_lumped = True
    run_import_transects = False
    run_import_losses = False

if post_process_swmm == "YES":
    run_post_processing = True
else:
    run_post_processing = False

if post_process_lump == "YES":
    run_lumped_post_processing = True
else:
    run_lumped_post_processing = False

if write_swmm_to_dss == "YES":
    run_swmm_to_dss = True
else:
    run_swmm_to_dss = False

if run_hspf_swmm == "NO" and run_lumped == "NO" and run_hspf_hru == "NO" and \
   post_process_swmm == "NO" and post_process_lump == "NO" and write_swmm_to_dss == "NO":
    print("No Operations Selected Program Exiting")
    # sys.exit()

if post_process_swmm:
    events_swmm = events[events['StartDate']>=start_date_swmm]
    events_swmm = events_swmm[events_swmm['EndDate'] <= stop_date_swmm]
if post_process_lump:
    events_lumped = events[events['StartDate'] >= start_date_lumped]
    events_lumped = events_lumped[events_lumped['EndDate'] <= stop_date_lumped]

rgs = [rain_gage]
if run_post_processing or run_lumped_post_processing:
    if len(swmm_link) > 1:
        simulated_link_names = swmm_link
        monitor_location_ids = gage_location_id
        plot_titles = locations_title_for_plots
    else:
        simulated_link_names = [swmm_link.values[0]]
        monitor_location_ids = [gage_location_id.values[0]]
        plot_titles = [locations_title_for_plots.values[0]]

    simulated_rchres_names = [lumped_model_rchres]


precipitation_gage_h2_numbers_for_plots = rgs

# TODO need to update reporting block in swmm inp

for rg in rgs:
    emgaats_simulation_folder = emgaats_model_folder + "\\" + "sim"
    hspf_input_file_path = observed_data_folder
    observed_flow_file_path = observed_data_folder + "\\" + "ObservedFlow"
    swmm_input_file_path = emgaats_simulation_folder + "\\" + "SWMM"
    hspf_overlay_file_path = emgaats_simulation_folder + "\\" + "HSPF"
    swmm_simulation_file_path = emgaats_simulation_folder + "\\" + name + "_" + scenario + "_RG" + str(rg)
    hspf_simulation_file_path = swmm_simulation_file_path

    path_to_swmm_executable = swmm_exe_path
    path_to_hspf_executable = win_hspf_lt_path
    path_to_input_met_wdm_file = hspf_input_file_path
    path_to_input_uci_file = hspf_input_file_path

    name_of_hru_uci_file = "HRU_" + str(rg) + ".uci"
    name_of_lumped_uci_file = "Lumped_" + str(rg) + ".uci"
    name_of_input_met_wdm = "Met5min.wdm"
    name_of_unrouted_flow_wdm_file = "HRU" + str(rg) + ".wdm"
    name_of_routed_flow_wdm_file = "Lumped" + str(rg) + ".wdm"
    name_of_routed_flow_dss_file = "Lumped" + str(rg) + ".dss"
    name_of_swmm_inp_file = "SWMM.inp"
    name_of_swmm_out_file = "SWMM.out"
    name_of_swmm_rpt_file = "SWMM.rpt"
    name_of_swmm_dss_file = "SWMM2DSS.dss"

    input_met_wdm_file_path = path_to_input_met_wdm_file + "\\" + name_of_input_met_wdm
    input_swmm_inp_file_path = swmm_input_file_path + "\\" + name_of_swmm_inp_file

    simulation_input_met_wdm_file_path = hspf_simulation_file_path + "\\" + name_of_input_met_wdm
    simulation_unrouted_uci_file_path = hspf_simulation_file_path + "\\" + name_of_hru_uci_file
    simulation_routed_uci_file_path = hspf_simulation_file_path + "\\" + name_of_lumped_uci_file
    simulation_unrouted_flow_wdm_file_path = hspf_simulation_file_path + "\\" + name_of_unrouted_flow_wdm_file
    simulation_routed_flow_wdm_file_path = hspf_simulation_file_path + "\\" + name_of_routed_flow_wdm_file
    simulation_routed_flow_dss_file_path = hspf_simulation_file_path + "\\" + name_of_routed_flow_dss_file
    simulation_swmm_inp_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_inp_file
    simulation_swmm_out_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_out_file
    simulation_swmm_rpt_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_rpt_file
    dss_output_path = swmm_simulation_file_path + "\\" + name_of_swmm_dss_file

    input = hspf_overlay_file_path + r"\HSPFOverlay.csv"
    explicit_input = hspf_overlay_file_path + r"\HSPFOverlay.csv" #+ r"\HSPFExplicitOverlay.csv"
    interface = swmm_simulation_file_path + r"\hspf_to_swmm.txt"
    outlets = swmm_input_file_path + r"\SWMM.hspf.csv"
    explicit_subbasin_outlets = swmm_input_file_path + r"\explicit_areas_hspf.csv"
    summary_file = hspf_simulation_file_path + r"\subbasin_summary.csv"
    implnd_perlnd_file = hspf_simulation_file_path + r"\hspf_schematic_block.txt"
    subbasin_dataframe_output_file_path = hspf_simulation_file_path + r"\hspf_subbasin.xlsx"

    # create simulation folder if it does not exist
    print("Creating Simulation Folder")
    hspf_data_io.create_simulation_folder(swmm_simulation_file_path)

    if run_hru:
        print("HSPF hru run for SWMM")
        # copy uci to sim
        print("Copy Uci to Simulation")
        hspf_data_io.write_hspf_hru_uci_to_file(hspf, simulation_unrouted_uci_file_path, description, rg,
                                                hspf_start_date_hru, hspf_stop_date_hru, rain_gage_multiplier,
                                                pan_evap_evapotranspiration)

        # copy input wdm to sim
        print("Copy Met Input WDM to Simulation")
        hspf_data_io.copy_met_data_wdm(input_met_wdm_file_path, simulation_input_met_wdm_file_path)

        # create blank_wdm
        print("Create Empty WDM for Unrouted HRU Flows")
        hspf_data_io.create_blank_unrouted_flow_wdm(hspf, simulation_unrouted_flow_wdm_file_path)

        # run hspf
        print("Run HSPF to Calculate Unrouted HRU Flows")
        progressbar = SimpleProgressBar()
        hspf_data_io.run_hspf(hspf_simulation_file_path, name_of_hru_uci_file, path_to_hspf_executable)
        progressbar.finish()

    if run_overlay:
        # run overlay to interface file
        print("Read Input Create Subbasins and Outlets")
        progressbar = SimpleProgressBar()
        hspf.wdm_file = simulation_unrouted_flow_wdm_file_path
        hspf.read_input_file(input, include_impervious=include_impervious, predevelopment=predeveloped)
        hspf.read_new_outlet_file(outlets)
        hspf.create_explicit_impervious_area_subbasins(explicit_subbasin_outlets, explicit_input, include_impervious=include_impervious)
        hspf.create_unique_outlets()
        subbasin_text = hspf_data_io.write_hspf_schematic_block_individual_subbasins_text(hspf, hspf.subbasins)
        subbasin_dataframe = hspf_data_io.write_individual_subbasins_to_dataframe(hspf, hspf.subbasins)
        subbasin_dataframe.to_excel(subbasin_dataframe_output_file_path)

        progressbar.finish()

        print("Read HRU Flows")
        progressbar = SimpleProgressBar()
        hspf.create_hru_base_flow_dataframe()
        hspf.create_hru_inter_flow_dataframe()
        hspf.create_hru_surface_flow_dataframe()
        progressbar.finish()

        print("Calculate Flows")
        progressbar = SimpleProgressBar()
        hspf.calculate_areas_for_outlets()
        hspf.calculate_flow_at_each_outlet()
        hspf.create_outlet_flow_dataframe()
        progressbar.finish()

        print("Write Interface File and Summary Files")
        progressbar = SimpleProgressBar()
        hspf_data_io.write_interface_file(hspf, interface)
        hspf_data_io.write_subbasins_summary_file(hspf, summary_file)
        progressbar.finish()

    if run_hspf_lumped:
        if not run_overlay:
            print("Read Input Create Subbasins and Outlets")
            progressbar = SimpleProgressBar()
            # copy input wdm to sim
            print("Copy Met Input WDM to Simulation")
            hspf_data_io.copy_met_data_wdm(input_met_wdm_file_path, simulation_input_met_wdm_file_path)
            hspf.wdm_file = simulation_unrouted_flow_wdm_file_path
            hspf.read_input_file(input, predevelopment=predeveloped)
            hspf.read_new_outlet_file(outlets)
            hspf.create_explicit_impervious_area_subbasins(explicit_subbasin_outlets, explicit_input)
            hspf.create_unique_outlets()
            progressbar.finish()

        # copy obs flow to sim
        try:
            filtered_monitor_dss = observed_flow_file_path + "\\" + str(monitor_location_ids[0]) + ".dss"
            hspf_data_io.copy_obs_data_dss(filtered_monitor_dss, simulation_routed_flow_dss_file_path)
        except:
            print("Could not copy observed flow dss file.")

        # copy input wdm to sim
        print("Copy Met Input WDM to Simulation")
        hspf_data_io.copy_met_data_wdm(input_met_wdm_file_path, simulation_input_met_wdm_file_path)

        # create blank_wdm
        print("Create Empty WDM for Lumped Model Routed Flows")
        hspf_data_io.create_blank_routed_flow_wdm(hspf, simulation_routed_flow_wdm_file_path)

        hspf_data_io.write_hspf_uci_to_file(hspf, simulation_routed_uci_file_path, name, description, rg,
                                            hspf_start_date_lumped, hspf_stop_date_lumped, rain_gage_multiplier,
                                            pan_evap_evapotranspiration)

        # run hspf
        print("Run HSPF to Calculate Lump Model Routed Flows")
        progressbar = SimpleProgressBar()
        hspf_data_io.run_hspf(hspf_simulation_file_path, name_of_lumped_uci_file, path_to_hspf_executable)
        progressbar.finish()

    if run_swmm:
        # copy swmm inp file
        print("Copy SWMM inp")
        progressbar = SimpleProgressBar()
        hspf_data_io.copy_swmm_inp(input_swmm_inp_file_path, simulation_swmm_inp_file_path, swmm_start_date, swmm_stop_date,
                                   routing_time_step=routing_time_step_in_seconds,
                                   all_links=all_links_in_swmm_output_file,
                                   links_to_report=simulated_link_names)
        if run_import_transects:
            print("Importing Transects")
            TransectsMain([emgaats_model_folder, simulation_swmm_inp_file_path])
        if run_import_losses:
            print("Importing Losses")
            LossesMain([emgaats_model_folder, simulation_swmm_inp_file_path])
        progressbar.finish()
        # run swmms
        progressbar = SimpleProgressBar()
        hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                              name_of_swmm_out_file, path_to_swmm_executable)
        hspf_data_io.write_swmm_ini_file(swmm_simulation_file_path)
        progressbar.finish()
        total_progressbar.finish()

    if run_post_processing or run_lumped_post_processing:
        if run_post_processing and run_lumped_post_processing:
            post_processing = ["Lumped", "SWMM"]
        elif run_post_processing:
            post_processing = ["SWMM"]
        else:
            post_processing = ["Lumped"]

        for post in post_processing:
            if post == "Lumped":
                run_post_processing = False
                run_lumped_post_processing = True
                events = events_lumped
                print("Running Lumped model post processing")
            elif post == "SWMM":
                run_post_processing = True
                run_lumped_post_processing = False
                events = events_swmm
                print("Running HSPF/SWMM model post processing")

            simulated_data_sets = []
            observed_data_sets = []
            print("Getting observed and simulated data")
            if run_post_processing:
                for simulated_link_name in simulated_link_names:
                    simulated_data = SimulatedData(link_name=simulated_link_name)
                    simulated_data.get_sim_flow_data(simulation_swmm_out_file_path)
                    simulated_data.filtered_time_step = 5 #TODO get timestep
                    simulated_data_sets.append(simulated_data)
            elif run_lumped_post_processing:
                for simulated_RCHRES_name in simulated_rchres_names:
                    simulated_data = SimulatedData(link_name="RCHRES 1") #TODO not hardwired
                    simulated_data.flow_data = hspf_data_io.read_lumped_model_flow_data(simulation_routed_flow_wdm_file_path,
                                                                                    1010)
                    simulated_data.filtered_time_step = 5
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
            if run_post_processing:
                for index, simulated_link_name in enumerate(simulated_link_names):
                    simulated_data = simulated_data_sets[index].flow_data
                    observed_data = observed_data_sets[index].filtered_flow_data
                    long_term_statistics = simulated_data_sets[index].filter_data_based_on_data_from_another_source(simulated_data, observed_data)
                    simulated_data_sets[index].filtered_flow_data = long_term_statistics  # TODO clean this up
            elif run_lumped_post_processing:
                for index, simulated_link_name in enumerate(simulated_rchres_names):
                    simulated_data = simulated_data_sets[index].flow_data
                    observed_data = observed_data_sets[index].filtered_flow_data
                    long_term_statistics = simulated_data_sets[index].filter_data_based_on_data_from_another_source(simulated_data, observed_data)
                    simulated_data_sets[index].filtered_flow_data = long_term_statistics  # TODO clean this up

            precipitation_gages = []
            print("Precipitation data")
            for gage in precipitation_gage_h2_numbers_for_plots:
                precipitation_gage = PrecipitationGage(gage)
                precipitation_gage.read_raw_data_from_wdm(input_met_wdm_file_path)
                precipitation_gage.read_filled_data_from_wdm(input_met_wdm_file_path)
                precipitation_gages.append(precipitation_gage)

            # if interactive:
            #     figure_data_review = CalibrationDataReview(plot_start_date, plot_stop_date, precipitation_gages, observed_data_sets, simulated_data_sets)
            #     figure_data_review.create_figure()
            #     figure_data_review.show()

            if not events.empty:
                #print("Plotting entire plotting period (This will take a few minutes)")
                if run_post_processing:
                    pp = PdfPages(swmm_simulation_file_path + "\\" + name + "_RG" + str(rg) + '_events_plots.pdf')
                elif run_lumped_post_processing:
                    pp = PdfPages(swmm_simulation_file_path + "\\" + name + "_RG" + str(rg) + '_lumped_events_plots.pdf')
                if run_post_processing:
                    file_path = swmm_simulation_file_path + "\\" + name + "_" + str(rg) + "_" + "long_term_and_events.xlsx"
                elif run_lumped_post_processing:
                    file_path = swmm_simulation_file_path + "\\" + name + "_" + str(rg) + "_" + "lumped_long_term_and_events.xlsx"

                with pd.ExcelWriter(file_path) as writer:
                    monitor_location_index = -1
                    for simulated_data_set, observed_data_set in zip(simulated_data_sets, observed_data_sets):
                        monitor_location_index += 1
                        monitor_location = observed_data_set.location_id
                        link_name = simulated_data_set.link_name
                        print("Link_name:" + link_name)
                        event_dicts = []
                        #figure_data_review = CalibrationDataReview(plot_start_date, plot_stop_date,
                        #                                           precipitation_gages, [observed_data_sets[monitor_location_index]],
                        #                                           [simulated_data_sets[monitor_location_index]], title=plot_title[monitor_location_index])
                        #figure_data_review.create_figure()
                        #figure_data_review.write_to_pdf(pp)
                        #figure_data_review.close()
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
                        observed_data = observed_data_sets[monitor_location_index].filtered_flow_data[observed_data_sets[monitor_location_index].filtered_flow_data > 0]
                        observed_data = observed_data.rename(columns={observed_data.columns[0]: "Obs flow"})
                        long_term_statistics = simulated_data_sets[monitor_location_index].flow_data

                        simulated = long_term_statistics.copy(deep=True)
                        long_term_statistics = simulated_data_sets[monitor_location_index].filter_data_based_on_data_from_another_source(simulated_data, observed_data)

                        simulated_data_sets[monitor_location_index].filtered_flow_data = long_term_statistics  # TODO clean this up
                        long_term_statistics = long_term_statistics.join(observed_data)
                        obs = long_term_statistics.copy(deep=True)

                        flow = obs.copy(deep=True)
                        volume = flow*5*60/43560
                        #flow = flow.mean().T
                        volume = volume.sum().T
                        volume['% Diff'] = (volume[0] - volume[1])/volume[1] * 100
                        percent_diff_labels_total = ['{0:.1f}%'.format(flt).replace('nan%','') for flt in [volume['% Diff']]]
                        volume.to_excel(writer, sheet_name='Total_Vol_' + link_name, float_format="%0.2f", header=False)
                        total_vol_bar_chart_plot = TotalVolumeFlowBarChart([volume["Obs flow"]],
                                                                         [volume["Sim flow"]],
                                                                         ["Total Volume"],
                                                                         percent_difference_labels= percent_diff_labels_total,
                                                                         title="Total Volume\n" + plot_titles[monitor_location_index]
                                                                         )
                        total_vol_bar_chart_plot.create_figure()
                        total_vol_bar_chart_plot.write_to_pdf(pp)
                        total_vol_bar_chart_plot.close()

                        # long_term_statistics = simulated_data_sets[monitor_location_index].compare_avg_data_per_water_year(simulated_data, observed_data)
                        long_term_statistics = simulated_data_sets[
                            monitor_location_index].compare_total_volume_data_per_water_year(simulated_data, observed_data)
                        if long_term_statistics is not None:
                            wy = long_term_statistics.copy(deep=True)
                            wy['% Diff'] = (wy[wy.columns[0]] - wy[wy.columns[1]])/wy[wy.columns[1]] * 100
                            percent_diff_labels_wy = ['{0:.1f}%'.format(flt).replace('nan%', '') for flt in
                                                   wy['% Diff']]
                            wy.to_excel(writer, sheet_name='Avg_WY_Vol_' + link_name, float_format="%0.2f")
                            wy_flow_bar_chart_plot = TotalVolumeFlowBarChart(wy["Obs flow"].values,
                                                                                wy["Sim flow"].values,
                                                                                wy.index.values,
                                                                                percent_difference_labels=percent_diff_labels_wy,
                                                                                title="WY Volume\n" + plot_titles[monitor_location_index]
                                                                                )
                            wy_flow_bar_chart_plot.create_figure()
                            wy_flow_bar_chart_plot.write_to_pdf(pp)
                            wy_flow_bar_chart_plot.close()

                        # long_term_statistics = simulated_data_sets[monitor_location_index].compare_avg_data_per_month(simulated_data, observed_data)
                        long_term_statistics = simulated_data_sets[monitor_location_index].compare_total_volume_data_per_month(
                            simulated_data, observed_data)
                        monthly_avg = long_term_statistics.copy(deep=True)

                        monthly_avg['% Diff'] = (monthly_avg[monthly_avg.columns[0]] - monthly_avg[monthly_avg.columns[1]])/monthly_avg[monthly_avg.columns[1]] * 100
                        percent_diff_labels_monthly = ['{0:.1f}%'.format(flt).replace('nan%', '') for flt in
                                                           monthly_avg['% Diff']]

                        monthly = monthly_avg.copy(deep=True)
                        if not monthly.empty: #TODO should this be obs
                            monthly = monthly.groupby([monthly.index.month]).mean()
                            monthly['% Diff'] = (monthly[monthly.columns[0]] - monthly[monthly.columns[1]])/monthly[monthly.columns[1]] * 100
                            monthly.index.name = "Month"
                            monthly.to_excel(writer, sheet_name='Avg_Mon_Vol_' + link_name, float_format="%0.2f")
                            monthly_avg.to_excel(writer, sheet_name='Avg_Mon_Vol_By_Yr_' + link_name, float_format="%0.2f")

                            percent_diff_labels_avg_monthly = ['{0:.1f}%'.format(flt).replace('nan%', '') for flt in monthly['% Diff']]
                            monthly_avg_vol_bar_chart_plot = TotalVolumeFlowBarChart(monthly["Obs flow"].values,
                                                                                     monthly["Sim flow"].values,
                                                                                     monthly.index.values,
                                                                                     percent_difference_labels=percent_diff_labels_avg_monthly,
                                                                                     title="Average Monthly Volume\n" + plot_titles[
                                                                                         monitor_location_index]
                                                                                     )
                            monthly_avg_vol_bar_chart_plot.create_figure()
                            monthly_avg_vol_bar_chart_plot.write_to_pdf(pp)
                            monthly_avg_vol_bar_chart_plot.close()

                            monthly_flow_bar_chart_plot = TotalVolumeFlowBarChart(monthly_avg["Obs flow"].values,
                                                                                     monthly_avg["Sim flow"].values,
                                                                                     monthly_avg.index.strftime(
                                                                                         "%m-%y").values,
                                                                                     percent_difference_labels=percent_diff_labels_monthly,
                                                                                     title="Monthly Volume\n" + plot_titles[
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

                            obs_peak_flow = events_statistics["Obs_Peak_Flow"].values
                            sim_peak_flow = events_statistics["Sim_Peak_Flow"].values
                            res_peak_flow = stats.linregress(obs_peak_flow, sim_peak_flow)
                            obs_volume = events_statistics["Obs_Volume"].values
                            sim_volume = events_statistics["Sim_Volume"].values
                            res_volume = stats.linregress(obs_volume, sim_volume)
                            peak_flow_scatter_plot = CalibrationPeakFlowDataReview(events_statistics["Obs_Peak_Flow"].values,
                                                                                   events_statistics["Sim_Peak_Flow"].values,
                                                                                   events_statistics["Obs_Volume"].values,
                                                                                   events_statistics["Sim_Volume"].values,
                                                                                   peak_flow_res=res_peak_flow,
                                                                                   volume_res=res_volume,
                                                                                   title=plot_titles[monitor_location_index])
                            peak_flow_scatter_plot.create_figure()
                            peak_flow_scatter_plot.write_to_pdf(pp)
                            peak_flow_scatter_plot.close()

                for index, event in events.iterrows():
                    print("Plotting event:" + str(event.StartDate))
                    try:
                        for index, simulated_data in enumerate(simulated_data_sets):
                            if event[observed_data_sets[index].location_id] == "YES":
                                observed_data_sets_1 = [observed_data_sets[index]]
                                simulated_data_sets_1 = [simulated_data]
                                event_start_date = event.StartDate
                                event_stop_date = event.EndDate
                                simulated_peak_flow = simulated_data_sets_1[0].peak_filtered_flow(event_start_date, event_stop_date)
                                observed_peak_flow = observed_data_sets_1[0].peak_filtered_flow(event_start_date, event_stop_date)
                                observed_peak_raw_flow = observed_data_sets_1[0].peak_flow(event_start_date,
                                                                                                event_stop_date)
                                if simulated_peak_flow > observed_peak_raw_flow:
                                    max_flow = simulated_peak_flow
                                else:
                                    max_flow = observed_peak_raw_flow

                                if max_flow > 10:
                                    max_flow = math.ceil(max_flow / 10) * 10
                                else:
                                    max_flow = math.ceil(max_flow)
                                if not observed_data_sets_1[0].filtered_flow_data.loc[event_start_date: event_stop_date].empty:
                                    figure_data_review = CalibrationDataReview(event_start_date, event_stop_date,
                                                                               precipitation_gages, observed_data_sets_1,
                                                                               simulated_data_sets_1, title=plot_titles[index],
                                                                               peak_flow=max_flow)
                                else:
                                    simulated_data_dummy = copy.deepcopy(simulated_data_sets_1[0])
                                    simulated_data_dummy.filtered_flow_data = simulated_data_dummy.flow_data
                                    simulated_data_dummy.flow = True
                                    simulated_data_dummy.depth = False
                                    simulated_data_dummy.velocity = False
                                    simulated_data_dummy.node_name = ""
                                    dummy_simulated_data_sets_1 = [simulated_data_dummy]
                                    max_flow = simulated_data_dummy.peak_flow(event_start_date, event_stop_date)
                                    figure_data_review = CalibrationDataReview(event_start_date, event_stop_date,
                                                                               precipitation_gages, None,
                                                                               dummy_simulated_data_sets_1, title=plot_titles[index],
                                                                               peak_flow=max_flow)
                                figure_data_review.create_figure()
                                figure_data_review.write_to_pdf(pp)
                                figure_data_review.close()
                    except Exception:
                        traceback_output = traceback.format_exc()
                        print("Failed to create plot")
                        print(traceback_output)
                        print(plot_titles[index])
                        print(event_start_date)

                pp.close()
    if run_lumped_post_processing:
        data_io = BaseDataIo()
        os.chdir(swmm_simulation_file_path)
        basin_name = "Tryon"
        dss_path = "/" + basin_name + "/" + "RCHRES1" + "/FLOW//5MIN/SIM" + scenario + "/"
        dsn = 1010
        flow_df = hspf_data_io.read_lumped_model_flow_data(simulation_routed_flow_wdm_file_path, dsn)
        data_io.write_5_minute_filtered_flow_to_regular_dss(simulation_routed_flow_dss_file_path,
                                                            dss_path,
                                                            flow_df)

    if run_swmm_to_dss:
        data_io = BaseDataIo()
        links_df = swmmtoolbox.listdetail(simulation_swmm_out_file_path, 'link')
        os.chdir(swmm_simulation_file_path)
        simulation_routed_flow_dss_file_path = r"SWMM2DSS.dss"
        for link in links_df.itertuples():
            link_name = link[1]
            basin_name = "Tryon"
            dss_path = "/" + basin_name + "/" + str(link_name) + "/FLOW//5MIN/SIM" + scenario + "/"
            flow_df = swmmtoolbox.extract(simulation_swmm_out_file_path, ['link', link_name, 'Flow_rate'])
            data_io.write_5_minute_filtered_flow_to_regular_dss(simulation_routed_flow_dss_file_path,
                                                                dss_path,
                                                                flow_df)
    if run_obs_to_dss:
        data_io = BaseDataIo()
        os.chdir(swmm_simulation_file_path)
        obs_flow_dss_file_path = r"SWMM2DSS.dss"
        for monitor_location in monitor_location_ids:
            filtered_monitor_file = observed_flow_file_path + "\\" + "filtered" + str(monitor_location) + ".h5"
            monitor_file = observed_flow_file_path + "\\" + "raw" + str(monitor_location) + ".h5"
            temporary_flow_monitor = TemporaryFlowMonitorData(monitor_location, flow=True)
            temporary_flow_monitor.get_filtered_flow_data_from_hdf5(filtered_monitor_file)
            temporary_flow_monitor.get_flow_data_from_hdf5(monitor_file)

            basin_name = "Tryon"
            dss_path = "/" + basin_name + "/" + str(monitor_location) + "/FLOW//IR-DECADE/OBS" + "/"
            flow_df = temporary_flow_monitor.flow_data
            data_io.write_raw_flow_data_to_irregular_dss(simulation_routed_flow_dss_file_path,
                                                                dss_path,
                                                                flow_df)
            dss_path = "/" + basin_name + "/" + str(monitor_location) + "/FLOW//5MIN/OBSFiltered" + "/"
            filtered_flow_df = temporary_flow_monitor.filtered_flow_data.resample('5min').obj.fillna(-901)
            data_io.write_5_minute_filtered_flow_to_regular_dss(simulation_routed_flow_dss_file_path,
                                                                dss_path,
                                                                filtered_flow_df)
