from hspf.businessclasses.hspf import Hspf
from hspf.dataio.hspf_dataio import HspfDataIo
from common.simpleprogressbar import SimpleProgressBar
from PyQt5.QtWidgets import QApplication
from common.file_dialog import App
from swmm.transects.swmm_transects_main import main as TransectsMain
from swmm.losses.swmm_losses_main import main as LossesMain
from swmm_to_ftable import stage_storage_flow
import pandas as pd
import sys
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

else:
    print("No file Selected.")
    sys.exit()

emgaats_model_folder, win_hspf_lt_path, swmm_exe_path, observed_data_folder = hspf_data_io.read_file_paths()

rain_gage, rain_gage_multiplier, pan_evap_evapotranspiration = hspf_data_io.read_precip_and_evap()

run_hspf = True
run_overlay = True
run_swmm = True
run_import_transects = True
run_import_losses = True
# run_post_process_results_gdb = False


storms = {'D25yr24hrSCS': (2025, [1]),
          'D10yr24hrSCS': (2010, [1]),
          'WQ': (2000, [1, 0.5, 0.2, 0.1, 0.05, 0.01]),
          'D02yr24hrSCS': (2002, [1]),
          'D05yr24hrSCS': (2005, [1]),
          'D100yr24hrSCS': (2100, [1, 2, 5]),
          }


start_date = "1/1/2000"
stop_date = "1/4/2000"
hspf_start_date_hru = "1998 10 01"
hspf_stop_date_hru = "2000 01 03"

overlay_has_not_run = True

ftable_excel_file_path = r"C:\Users\sggho\Documents\HSPFModels\Models\TryonMainstemSimple\Ftable.xlsx"
xl = pd.ExcelFile(ftable_excel_file_path)
ftable_worksheets = xl.sheet_names
ftable_input_data_sets_dict = {}
ftable_output_data_sets_dict = {}
for ftable_worksheet in ftable_worksheets:
    ftable_input_data_sets_dict[ftable_worksheet] = xl.parse(ftable_worksheet)
    ftable_output_data_sets_dict[ftable_worksheet] = []
for storm in storms.keys():
    print("Running " + storm + " design storm.")

    description = storm
    factors = storms[storm][1]
    for factor in factors:
        emgaats_simulation_folder = emgaats_model_folder + "\\" + "sim"
        hspf_input_file_path = observed_data_folder
        swmm_input_file_path = emgaats_simulation_folder + "\\" + "SWMM"
        hspf_overlay_file_path = emgaats_simulation_folder + "\\" + "HSPF"
        swmm_simulation_file_path = emgaats_simulation_folder + "\\" + storm + "_" + str(factor)
        hspf_simulation_file_path = swmm_simulation_file_path

        path_to_swmm_executable = swmm_exe_path
        path_to_hspf_executable = win_hspf_lt_path
        path_to_input_met_wdm_file = hspf_input_file_path
        path_to_input_uci_file = hspf_input_file_path

        name_of_hru_uci_file = "HRU_" + storm + ".uci"
        name_of_input_met_wdm = "DesignStorm5min.wdm"
        name_of_unrouted_flow_wdm_file = "HRU" + storm + ".wdm"
        name_of_swmm_inp_file = "SWMM.inp"
        name_of_swmm_out_file = "SWMM.out"
        name_of_swmm_rpt_file = "SWMM.rpt"

        input_met_wdm_file_path = path_to_input_met_wdm_file + "\\" + name_of_input_met_wdm
        input_swmm_inp_file_path = swmm_input_file_path + "\\" + name_of_swmm_inp_file
        simulation_input_met_wdm_file_path = hspf_simulation_file_path + "\\" + name_of_input_met_wdm
        simulation_unrouted_uci_file_path = hspf_simulation_file_path + "\\" + name_of_hru_uci_file
        simulation_unrouted_flow_wdm_file_path = hspf_simulation_file_path + "\\" + name_of_unrouted_flow_wdm_file
        simulation_swmm_inp_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_inp_file
        simulation_swmm_out_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_out_file
        simulation_swmm_rpt_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_rpt_file

        input = hspf_overlay_file_path + r"\HSPFOverlay.csv"
        interface = swmm_simulation_file_path + r"\hspf_to_swmm.txt"
        outlets = swmm_input_file_path + r"\SWMM.hspf.csv"
        summary_file = hspf_simulation_file_path + r"\subbasin_summary.csv"
        implnd_perlnd_file = hspf_simulation_file_path + r"\hspf_schematic_block.txt"

        total_progressbar = SimpleProgressBar()

        hspf = Hspf(hspf_data_io)
        hspf.perlnds = hspf.create_perlnds(hspf_data_io.read_hspf_input_file_perlnds())
        hspf.implnds = hspf.create_implnds(hspf_data_io.read_hspf_input_file_implnds())

        hspf.start_date_time = start_date
        hspf.stop_date_time = stop_date

        if run_hspf:
            # create simulation folder if it does not exist
            print("Creating Simulation Folder")
            hspf_data_io.create_simulation_folder(swmm_simulation_file_path)

            # copy uci to sim
            print("Copy Uci to Simulation")
            hspf_data_io.write_hspf_design_storm_hru_uci_to_file(hspf, simulation_unrouted_uci_file_path, description, storm,
                                                                 hspf_start_date_hru, hspf_stop_date_hru, rain_gage_multiplier,
                                                                 pan_evap_evapotranspiration)

            # copy input wdm to sim
            print("Copy Met Input WDM to Simulation")
            hspf_data_io.copy_met_data_wdm(input_met_wdm_file_path, simulation_input_met_wdm_file_path)

            # create blank_wdm
            print("Create Empty WDM for Unrouted HRU Flows")
            hspf_data_io.create_blank_unrouted_flow_wdm(hspf, simulation_unrouted_flow_wdm_file_path)

            # copy swmm inp file
            print("Copy SWMM inp")
            progressbar = SimpleProgressBar()
            hspf_data_io.copy_swmm_inp(input_swmm_inp_file_path, simulation_swmm_inp_file_path,
                                       start_date, stop_date, all_links=True, all_nodes=True)
            if run_import_transects:
                print("Importing Transects")
                TransectsMain([emgaats_model_folder, simulation_swmm_inp_file_path])
            if run_import_losses:
                print("Importing Losses")
                LossesMain([emgaats_model_folder, simulation_swmm_inp_file_path])
            progressbar.finish()

            # run hspf
            print("Run HSPF to Calculate Unrouted HRU Flows")
            progressbar = SimpleProgressBar()
            hspf_data_io.run_hspf(hspf_simulation_file_path, simulation_unrouted_uci_file_path, path_to_hspf_executable)
            progressbar.finish()

        if run_overlay:
            # run overlay to interface file
            print("Read Input Create Subbasins and Outlets")
            progressbar = SimpleProgressBar()
            hspf.wdm_file = simulation_unrouted_flow_wdm_file_path
            hspf.read_input_file(input)
            hspf.read_new_outlet_file(outlets)
            hspf.create_unique_outlets()
            progressbar.finish()
            overlay_has_not_run = False

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
            hspf_data_io.write_interface_file_for_ftable_creation(hspf, interface, factor)
            hspf_data_io.write_subbasins_summary_file(hspf, summary_file)
            progressbar.finish()

        if run_swmm:
            # run swmm
            progressbar = SimpleProgressBar()

            hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                                  name_of_swmm_out_file, path_to_swmm_executable)
            hspf_data_io.write_swmm_ini_file(swmm_simulation_file_path)
            progressbar.finish()
        for ftable in ftable_input_data_sets_dict.keys():
            ftable_output_dict = {}
            storage_node_names = list(ftable_input_data_sets_dict[ftable]['StorageNodes'].dropna().values)
            storage_link_names = list(ftable_input_data_sets_dict[ftable]['StorageLinks'].dropna().values)
            if ftable_input_data_sets_dict[ftable]['OutfallLinks'].dropna().empty:
                outfall_link_names = None
            else:
                outfall_link_names = list(ftable_input_data_sets_dict[ftable]['OutfallLinks'].dropna().values)
            if ftable_input_data_sets_dict[ftable]['OutfallNodes'].dropna().empty:
                outfall_node_names = None
            else:
                outfall_node_names = list(ftable_input_data_sets_dict[ftable]['OutfallNodes'].dropna().values)
            depth_node = ftable_input_data_sets_dict[ftable]['DepthNode'].values[0]
            total_volume, \
            outfall_link_flows, outfall_node_flows, \
            depth = stage_storage_flow(simulation_swmm_out_file_path,
                                       storage_link_names, storage_node_names,
                                       outfall_link_names, outfall_node_names,
                                       depth_node)
            ftable_output_dict['Depth'] = depth
            ftable_output_dict['Volume'] = total_volume
            if outfall_link_flows is None:
                print("No Outfall Links")
            else:
                for outfall_link_flow, outfall_link_name in zip(outfall_link_flows, outfall_link_names):
                    ftable_output_dict[outfall_link_name] = outfall_link_flow
            if outfall_node_flows is None:
                print("No Outfall Nodes")
            else:
                for outfall_node_flow, outfall_node_name in zip(outfall_node_flows, outfall_node_names):
                    ftable_output_dict[outfall_node_name] = outfall_node_flow
            ftable_output_data_sets_dict[ftable].append(ftable_output_dict)
for ftable in ftable_input_data_sets_dict.keys():
    ftable_df = pd.DataFrame(ftable_output_data_sets_dict[ftable]).sort_values(by=['Depth'], ignore_index=True)
    print(ftable_df)
    ftable_df.to_excel(r"C:\Users\sggho\Documents\HSPFModels\Models\TryonMainstemSimple\ftableout.xlsx")
    total_progressbar.finish()
sys.exit()
