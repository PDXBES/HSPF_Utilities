from hspf.businessclasses.hspf import Hspf
from hspf.dataio.hspf_dataio import HspfDataIo
from common.simpleprogressbar import SimpleProgressBar
from PyQt5.QtWidgets import QApplication
from common.file_dialog import App
from swmm.transects.swmm_transects_main import main as TransectsMain
from swmm.losses.swmm_losses_main import main as LossesMain

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
predevelopment = False

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

if predevelopment:
    storms = {'PreD25yr24hrSCS': 2025, #TODO should be enumeration
              'PreD10yr24hrSCS': 2010,
              'PreWQ': 2000,
              'Pre1_2_D02yr24hrSCS': 2002,
              'PreD02yr24hrSCS': 2002,
              'PreD05yr24hrSCS': 2005,
              'PreD100yr24hrSCS': 2100
              }
else:
    storms = {'D25yr24hrSCS': 2025, #TODO should be enumeration
              'D10yr24hrSCS': 2010,
              'WQ': 2000,
              '1_2_D02yr24hrSCS': 2002,
              'D02yr24hrSCS': 2002,
              'D05yr24hrSCS': 2005,
              'D100yr24hrSCS': 2100
              }

start_date = "1/1/2000"
stop_date = "1/4/2000"
hspf_start_date_hru = "1998 10 01"
hspf_stop_date_hru = "2000 01 03"

overlay_has_not_run = True

# TODO need to update reporting block in swmm inp

for storm in storms.keys():
    print("Running " + storm + " design storm.")

    description = storm
    emgaats_simulation_folder = emgaats_model_folder + "\\" + "sim"
    hspf_input_file_path = observed_data_folder
    swmm_input_file_path = emgaats_simulation_folder + "\\" + "SWMM"
    hspf_overlay_file_path = emgaats_simulation_folder + "\\" + "HSPF"
    swmm_simulation_file_path = emgaats_simulation_folder + "\\" + storm
    hspf_simulation_file_path = swmm_simulation_file_path

    path_to_swmm_executable = swmm_exe_path
    path_to_hspf_executable = win_hspf_lt_path
    path_to_input_met_wdm_file = hspf_input_file_path
    path_to_input_uci_file = hspf_input_file_path

    name_of_hru_uci_file = "HRU_" + storm + ".uci"
    name_of_input_met_wdm = "DesignStorm5min.wdm"  # TODO Change to design storm
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
    explicit_input = hspf_overlay_file_path + r"\HSPFExplicitOverlay.csv"
    explicit_input = input
    interface = swmm_simulation_file_path + r"\hspf_to_swmm.txt"
    outlets = swmm_input_file_path + r"\SWMM.hspf.csv"
    explicit_subbasin_outlets = swmm_input_file_path + r"\explicit_areas_hspf.csv"
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
                                                             pan_evap_evapotranspiration, predevelopment)

        # copy input wdm to sim
        print("Copy Met Input WDM to Simulation")
        hspf_data_io.copy_met_data_wdm(input_met_wdm_file_path, simulation_input_met_wdm_file_path)

        # create blank_wdm
        print("Create Empty WDM for Unrouted HRU Flows")
        hspf_data_io.create_blank_unrouted_flow_wdm(hspf, simulation_unrouted_flow_wdm_file_path)

        # copy swmm inp file
        print("Copy SWMM inp")
        progressbar = SimpleProgressBar()
        hspf_data_io.copy_swmm_inp(input_swmm_inp_file_path, simulation_swmm_inp_file_path, start_date, stop_date, '00:00:30')
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
        hspf.read_input_file(input, predevelopment)
        try:
            hspf.read_new_outlet_file(outlets)
        except:
            print("No lumped subbasins")
        hspf.create_explicit_impervious_area_subbasins(explicit_subbasin_outlets, explicit_input, predevelopment)
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
        if description == "1_2_D02yr24hrSCS":
            hspf_data_io.write_interface_file_half_flow(hspf, interface)
        else:
            hspf_data_io.write_interface_file(hspf, interface)
        hspf_data_io.write_subbasins_summary_file(hspf, summary_file)
        progressbar.finish()

    if run_swmm:
        # run swmm
        progressbar = SimpleProgressBar()

        hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                              name_of_swmm_out_file, path_to_swmm_executable)
        hspf_data_io.write_swmm_ini_file(swmm_simulation_file_path)
        progressbar.finish()

    # if run_post_process_results_gdb:
    #     extract_results = r"\\besfile1\asm_apps\apps\emgaats3\emg\emg extract --resultsfile " + swmm_simulation_file_path + "\\SWMM.rpt"
    #     subprocess.Popen(extract_results, shell=True)
    total_progressbar.finish()
sys.exit()
