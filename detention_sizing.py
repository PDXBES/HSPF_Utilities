# from hspf.businessclasses import hspf
from hspf.dataio import hspf_dataio
import pandas as pd
from swmmtoolbox import swmmtoolbox


def copy_swmm_inp(input_swmm_inp_file_path, rain_file_path, simulation_swmm_inp_file_path, return_period, roughness, depression_storage, curve_number, condition):
    with open(input_swmm_inp_file_path, 'r') as input_swmm_inp:
        inp = ""
        line = " "
        subcatchments = []
        while line is not '':
            line = input_swmm_inp.readline()
            if line[0:9] == "[OPTIONS]":
                inp += "[OPTIONS]\n" + \
                       ";;Option Value\n" + \
                       "FLOW_UNITS CFS\n" + \
                       "INFILTRATION CURVE_NUMBER\n" + \
                       "FLOW_ROUTING DYNWAVE\n" + \
                       "LINK_OFFSETS ELEVATION\n" + \
                       "MIN_SLOPE 0\n" + \
                       "ALLOW_PONDING YES\n" + \
                       "SKIP_STEADY_STATE NO\n" + \
                       "START_DATE           01/02/2000\n" + \
                       "START_TIME 12:00:00\n" + \
                       "REPORT_START_DATE    01/02/2000\n" + \
                       "REPORT_START_TIME 12:00:00\n" + \
                       "END_DATE             01/03/2000\n" + \
                       "END_TIME 12:00:00\n" + \
                       "SWEEP_START 01/01\n" + \
                       "SWEEP_END 12/31\n" + \
                       "DRY_DAYS 0\n" + \
                       "REPORT_STEP          00:00:30\n" + \
                       "WET_STEP 00:00:30\n" + \
                       "DRY_STEP 00:00:30\n" + \
                       "ROUTING_STEP 0:00:05\n" + \
                       "\n" + \
                       "INERTIAL_DAMPING PARTIAL\n" + \
                       "NORMAL_FLOW_LIMITED BOTH\n" + \
                       "FORCE_MAIN_EQUATION H-W\n" + \
                       "VARIABLE_STEP 0.75\n" + \
                       "LENGTHENING_STEP 0\n" + \
                       "MIN_SURFAREA 12.557\n" + \
                       "MAX_TRIALS 8\n" + \
                       "HEAD_TOLERANCE 0.005\n" + \
                       "SYS_FLOW_TOL 5\n" + \
                       "LAT_FLOW_TOL 5\n" + \
                       "MINIMUM_STEP 0.5\n" + \
                       "THREADS 6\n" + \
                       "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:7] == "[FILES]":
                inp += "[FILES]\n" + \
                       ";;Interfacing Files \n" + \
                       "SAVE OUTFLOWS " + condition + return_period + "outflow.txt\n" +\
                       "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:13] == "[EVAPORATION]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:10] == "[PATTERNS]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:11] == "[RAINGAGES]":
                inp += "[RAINGAGES]\n" + \
                       ";;Name           Format    Interval SCF  Source\n" + \
                       ";;-------------- --------- ------ ------ ----------\n" + \
                       "1                 VOLUME     0:05    1.0 TIMESERIES Rain" + return_period + "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:15]=="[SUBCATCHMENTS]":
                    inp += line
                    for i in range(2):
                        inp += input_swmm_inp.readline()
                    line = input_swmm_inp.readline()
                    while line is not '':
                        if not line == '\n':
                            tokens = line.split()
                            inp += tokens[0] + " " + tokens[1] + " " + tokens[2] + " " + tokens[3] + " " + "0.0" + " " + tokens[5] + " " + tokens[6] + " " + tokens[7] + "\n"
                            subcatchments.append(tokens[0])
                            line = input_swmm_inp.readline()
                        else:
                            inp += line
                            line = input_swmm_inp.readline()
                        if line[0] == "[":
                            break

            if line[0:10] == "[SUBAREAS]":
                inp += line
                for i in range(2):
                    inp += input_swmm_inp.readline()
                line = input_swmm_inp.readline()
                while line is not '':
                    if not line == '\n':
                        tokens = line.split()
                        inp += tokens[0] + " " + tokens[1] + " " + str(roughness) + " " + tokens[3] + " " + str(depression_storage) + " " + tokens[5] + " " + tokens[6] + "\n"
                        line = input_swmm_inp.readline()
                    else:
                        inp += line
                        line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break

            inp += line
        inp += "[INFILTRATION]\n" + \
                ";;Subcatchment   CurveNum              DryTime\n" + \
                ";;-------------- ---------- ---------- ----------\n"
        for subcatchment in subcatchments:
            inp += subcatchment + " " + str(curve_number) + " " + "0.5" + " " + "4" + "\n"

        inp += "\n"

        with open(rain_file_path, 'r') as rain_file:
            inp += rain_file.read()

        with open(simulation_swmm_inp_file_path, 'w') as output_swmm_inp:
            output_swmm_inp.write(inp)


def create_swmm_2_year_runoff_inp(input_swmm_inp_file_path, rain_file_path, simulation_swmm_inp_file_path, return_period, roughness, depression_storage, curve_number, condition):
    # subcatchments and nodes only
    # all nodes changed to outfalls
    with open(input_swmm_inp_file_path, 'r') as input_swmm_inp:
        inp = ""
        line = " "
        subcatchments = []
        while line is not '':
            line = input_swmm_inp.readline()
            if line[0:9] == "[OPTIONS]":
                inp += "[OPTIONS]\n" + \
                       ";;Option Value\n" + \
                       "FLOW_UNITS CFS\n" + \
                       "INFILTRATION CURVE_NUMBER\n" + \
                       "FLOW_ROUTING DYNWAVE\n" + \
                       "LINK_OFFSETS ELEVATION\n" + \
                       "MIN_SLOPE 0\n" + \
                       "ALLOW_PONDING YES\n" + \
                       "SKIP_STEADY_STATE NO\n" + \
                       "START_DATE           01/02/2000\n" + \
                       "START_TIME 12:00:00\n" + \
                       "REPORT_START_DATE    01/02/2000\n" + \
                       "REPORT_START_TIME 12:00:00\n" + \
                       "END_DATE             01/03/2000\n" + \
                       "END_TIME 12:00:00\n" + \
                       "SWEEP_START 01/01\n" + \
                       "SWEEP_END 12/31\n" + \
                       "DRY_DAYS 0\n" + \
                       "REPORT_STEP          00:00:30\n" + \
                       "WET_STEP 00:00:30\n" + \
                       "DRY_STEP 00:00:30\n" + \
                       "ROUTING_STEP 0:00:05\n" + \
                       "\n" + \
                       "INERTIAL_DAMPING PARTIAL\n" + \
                       "NORMAL_FLOW_LIMITED BOTH\n" + \
                       "FORCE_MAIN_EQUATION H-W\n" + \
                       "VARIABLE_STEP 0.75\n" + \
                       "LENGTHENING_STEP 0\n" + \
                       "MIN_SURFAREA 12.557\n" + \
                       "MAX_TRIALS 8\n" + \
                       "HEAD_TOLERANCE 0.005\n" + \
                       "SYS_FLOW_TOL 5\n" + \
                       "LAT_FLOW_TOL 5\n" + \
                       "MINIMUM_STEP 0.5\n" + \
                       "THREADS 6\n" + \
                       "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:7] == "[FILES]":
                inp += "[FILES]\n" + \
                       ";;Interfacing Files \n" + \
                       "SAVE OUTFLOWS " +  condition + return_period + "outflow.txt\n" +\
                       "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:13] == "[EVAPORATION]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:10] == "[PATTERNS]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:11] == "[RAINGAGES]":
                inp += "[RAINGAGES]\n" + \
                       ";;Name           Format    Interval SCF  Source\n" + \
                       ";;-------------- --------- ------ ------ ----------\n" + \
                       "1                 VOLUME     0:05    1.0 TIMESERIES Rain" + return_period + "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:15]=="[SUBCATCHMENTS]":
                    inp += line
                    for i in range(2):
                        inp += input_swmm_inp.readline()
                    line = input_swmm_inp.readline()
                    while line is not '':
                        if not line == '\n':
                            tokens = line.split()
                            inp += tokens[0] + " " + tokens[1] + " " + tokens[2] + " " + tokens[3] + " " + "0.0" + " " + tokens[5] + " " + tokens[6] + " " + tokens[7] + "\n"
                            subcatchments.append(tokens[0])
                            line = input_swmm_inp.readline()
                        else:
                            inp += line
                            line = input_swmm_inp.readline()
                        if line[0] == "[":
                            break

            if line[0:10] == "[SUBAREAS]":
                inp += line
                for i in range(2):
                    inp += input_swmm_inp.readline()
                line = input_swmm_inp.readline()
                while line is not '':
                    if not line == '\n':
                        tokens = line.split()
                        inp += tokens[0] + " " + tokens[1] + " " + str(roughness) + " " + tokens[3] + " " + str(depression_storage) + " " + tokens[5] + " " + tokens[6] + "\n"
                        line = input_swmm_inp.readline()
                    else:
                        inp += line
                        line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break

            inp += line
        inp += "[INFILTRATION]\n" + \
                ";;Subcatchment   CurveNum              DryTime\n" + \
                ";;-------------- ---------- ---------- ----------\n"
        for subcatchment in subcatchments:
            inp += subcatchment + " " + str(curve_number) + " " + "0.5" + " " + "4" + "\n"

        inp += "\n"

        with open(rain_file_path, 'r') as rain_file:
            inp += rain_file.read()

        with open(simulation_swmm_inp_file_path, 'w') as output_swmm_inp:
            output_swmm_inp.write(inp)


        hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                              name_of_swmm_out_file, path_to_swmm_executable)
        hspf_data_io.write_swmm_ini_file(swmm_simulation_file_path)


def create_swmm_1_2_year_inp(input_swmm_inp_file_path, simulation_swmm_inp_file_path, return_period, condition):
    with open(input_swmm_inp_file_path, 'r') as input_swmm_inp:
        inp = ""
        line = " "
        subcatchments = []
        while line is not '':
            line = input_swmm_inp.readline()
            if line[0:9] == "[OPTIONS]":
                inp += "[OPTIONS]\n" + \
                       ";;Option Value\n" + \
                       "FLOW_UNITS CFS\n" + \
                       "INFILTRATION CURVE_NUMBER\n" + \
                       "FLOW_ROUTING DYNWAVE\n" + \
                       "LINK_OFFSETS ELEVATION\n" + \
                       "MIN_SLOPE 0\n" + \
                       "ALLOW_PONDING YES\n" + \
                       "SKIP_STEADY_STATE NO\n" + \
                       "START_DATE           01/02/2000\n" + \
                       "START_TIME 12:00:00\n" + \
                       "REPORT_START_DATE    01/02/2000\n" + \
                       "REPORT_START_TIME 12:00:00\n" + \
                       "END_DATE             01/03/2000\n" + \
                       "END_TIME 12:00:00\n" + \
                       "SWEEP_START 01/01\n" + \
                       "SWEEP_END 12/31\n" + \
                       "DRY_DAYS 0\n" + \
                       "REPORT_STEP          00:00:30\n" + \
                       "WET_STEP 00:00:30\n" + \
                       "DRY_STEP 00:00:30\n" + \
                       "ROUTING_STEP 0:00:05\n" + \
                       "\n" + \
                       "INERTIAL_DAMPING PARTIAL\n" + \
                       "NORMAL_FLOW_LIMITED BOTH\n" + \
                       "FORCE_MAIN_EQUATION H-W\n" + \
                       "VARIABLE_STEP 0.75\n" + \
                       "LENGTHENING_STEP 0\n" + \
                       "MIN_SURFAREA 12.557\n" + \
                       "MAX_TRIALS 8\n" + \
                       "HEAD_TOLERANCE 0.005\n" + \
                       "SYS_FLOW_TOL 5\n" + \
                       "LAT_FLOW_TOL 5\n" + \
                       "MINIMUM_STEP 0.5\n" + \
                       "THREADS 6\n" + \
                       "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:7] == "[FILES]":
                inp += "[FILES]\n" + \
                       ";;Interfacing Files \n" + \
                       "USE INFLOWS " + condition + return_period + "inflow.txt\n" + \
                       "SAVE OUTFLOWS " + condition + return_period + "outflow.txt\n" +\
                       "\n"
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:13] == "[EVAPORATION]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:10] == "[PATTERNS]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:11] == "[RAINGAGES]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:15] == "[SUBCATCHMENTS]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break

            if line[0:10] == "[SUBAREAS]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break
            if line[0:14] == "[INFILTRATION]":
                while line is not '':
                    line = input_swmm_inp.readline()
                    if line[0] == "[":
                        break

            inp += line
        inp += "\n"

        with open(simulation_swmm_inp_file_path, 'w') as output_swmm_inp:
            output_swmm_inp.write(inp)


def half_the_two_runoff_interface_file(two_year_runoff_interface_file_path, half_two_year_runoff_interface_file_path):
    with open(two_year_runoff_interface_file_path, 'r') as two_year_runoff_interface_file:
        with open(half_two_year_runoff_interface_file_path, 'w') as half_two_year_runoff_interface_file_path:
            line = " "
            while not line[0:4] == "Node":
                half_two_year_runoff_interface_file_path.write(line)
                line = two_year_runoff_interface_file.readline()
                if line is '':
                    print("Problem with two year runoff interface file")
                    break
            half_two_year_runoff_interface_file_path.write(line)
            line = two_year_runoff_interface_file.readline()
            while line is not "":
                tokens = line.split()
                output_line = ""
                for token in tokens[0:7]:
                    output_line += token + " "
                output_line += str(float(tokens[7])/2) + "\n"
                half_two_year_runoff_interface_file_path.write(output_line)
                line = two_year_runoff_interface_file.readline()


def update_facility_inp(input_swmm_inp_file_path, simulation_swmm_inp_file_path, interface_file_path, area, orifice_size, facility_name, outfall_name):
    with open(input_swmm_inp_file_path, 'r') as input_swmm_inp:
        inp = input_swmm_inp.read()
        inp = inp.replace("#AREA#", str(area))
        inp = inp.replace("#ORIFICESIZE#", str(orifice_size/12))
        inp = inp.replace("#INTERFACEFILE#", str(interface_file_path))
        inp = inp.replace("#FACILITYNAME#", facility_name)
        inp = inp.replace("#OUTFALLNAME#", outfall_name)
    with open(simulation_swmm_inp_file_path, 'w') as output_swmm_inp:
        output_swmm_inp.write(inp)


def get_max_peak_outfall_flows(swmm_simulation_file_path, name_of_swmm_rpt_file, name_of_swmm_out_file, condition, return_period)->pd.DataFrame:
    input_swmm_rpt_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_rpt_file
    outfall_names = []
    max_flows = []
    column_name = condition + return_period
    with open(input_swmm_rpt_file_path, 'r') as input_swmm_inp:
        line = " "
        while line is not '':
            line = input_swmm_inp.readline()
            if line[0:27] == "  Outfall Loading Summary\n":
                for i in range(8):
                    line = input_swmm_inp.readline()
                while not line == '  -----------------------------------------------------------\n':
                    tokens = line.split()
                    outfall_name = tokens[0]
                    outfall_flow = swmmtoolbox.extract(swmm_simulation_file_path + "\\" + name_of_swmm_out_file, ["node", outfall_name, "Total_inflow"])
                    max_flow = outfall_flow.max()[0]
                    if max_flow == 0:
                        print("Outfall:" + outfall_name + " Maxflow for condition: " + condition + " return period: " + return_period + " is 0\n")
                    outfall_names.append(outfall_name)
                    max_flow_rpt = float(tokens[3])

                    max_flows.append(max_flow)
                    line = input_swmm_inp.readline()
    outfall_peaks_df = pd.DataFrame(index=outfall_names, columns=[column_name], data=max_flows)
    return outfall_peaks_df


def get_max_peak_outfall_flow_facility(swmm_simulation_file_path, name_of_swmm_rpt_file, name_of_swmm_out_file, outfall_name)->float:
    input_swmm_rpt_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_rpt_file
    max_flow = None
    with open(input_swmm_rpt_file_path, 'r') as input_swmm_inp:
        line = " "
        while line is not '':
            line = input_swmm_inp.readline()
            if line[0:27] == "  Outfall Loading Summary\n":
                for i in range(8):
                    line = input_swmm_inp.readline()
                while not line == '  -----------------------------------------------------------\n':
                    tokens = line.split()
                    outfall_name_summary = tokens[0]
                    if outfall_name_summary == outfall_name:
                        outfall_flow = swmmtoolbox.extract(swmm_simulation_file_path + "\\" + name_of_swmm_out_file,
                                                           ["node", outfall_name, "Total_inflow"])
                        max_flow = outfall_flow.max()[0]
                    line = input_swmm_inp.readline()
    return max_flow


path_to_swmm_executable ="C:\Temp\HSPFWorkShopMaterials\EXE\SWMM\swmm5.exe"
input_file = "detention.inp"
hspf_data_io = hspf_dataio.HspfDataIo(input_file)
predeveloped = {"condition": "predeveloped", "roughness": 0.15, "surface_storage": 0.1, "curve_number": 79}
developed = {"condition": "developed", "roughness": 0.011, "surface_storage": 0.10, "curve_number": 98}

scenarios = [predeveloped, developed]
return_periods = ["1_2_2yr", "5yr", "10yr", "25yr"]
swmm_simulation_file_path = r"V:\E11098_Council_Crest\model\ModelsUpdatedFieldWork\DetentionCurveNumber\sim\Detention1LowerRoughnessAndDepressionFiltered"
rain_file_path = swmm_simulation_file_path + "\\" + "TIMESERIES.txt"
input_swmm_inp_file_path = swmm_simulation_file_path + "\\" + "detention.inp"
input_facility_inp_file_path = swmm_simulation_file_path + "\\" + "facility.inp"

scenario_outfall_peaks = []
for scenario in scenarios:
    outfall_peaks = []
    peak_flow_df = None
    for return_period in return_periods:
        if not return_period == "1_2_2yr":
            name_of_swmm_inp_file = return_period + scenario["condition"] + ".inp"
            name_of_swmm_rpt_file = return_period + scenario["condition"] + ".rpt"
            name_of_swmm_out_file = return_period + scenario["condition"] + ".out"
            simulation_swmm_inp_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_inp_file
            copy_swmm_inp(input_swmm_inp_file_path, rain_file_path, simulation_swmm_inp_file_path, return_period,
                          scenario["roughness"], scenario["surface_storage"], scenario["curve_number"],
                          scenario["condition"])
            hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                                  name_of_swmm_out_file, path_to_swmm_executable)
            hspf_data_io.write_swmm_ini_file(swmm_simulation_file_path)
            peak_flow_df = get_max_peak_outfall_flows(swmm_simulation_file_path, name_of_swmm_rpt_file, name_of_swmm_out_file,
                                                      scenario["condition"], return_period)
        else:
            return_period_2yr = "2yr"
            name_of_swmm_inp_file = return_period_2yr + scenario["condition"] + ".inp"
            name_of_swmm_rpt_file = return_period_2yr + scenario["condition"] + ".rpt"
            name_of_swmm_out_file = return_period_2yr + scenario["condition"] + ".out"
            simulation_swmm_inp_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_inp_file
            name_of_swmm_inp_file = return_period_2yr + scenario["condition"] + ".inp"
            copy_swmm_inp(input_swmm_inp_file_path, rain_file_path, simulation_swmm_inp_file_path, return_period_2yr,
                          scenario["roughness"], scenario["surface_storage"], scenario["curve_number"],
                          scenario["condition"])
            hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                                  name_of_swmm_out_file, path_to_swmm_executable)
            two_year_interface_file_path = swmm_simulation_file_path + "\\" + scenario["condition"] + return_period_2yr + "outflow.txt"

            half_the_two_year_interface_file_path = swmm_simulation_file_path + "\\" + scenario["condition"] + "1_2_2yr" + "inflow.txt"
            name_of_swmm_half_the_two_year_inp_file = return_period + scenario["condition"] + ".inp"
            name_of_swmm_half_the_two_year_rpt_file = return_period + scenario["condition"] + ".rpt"
            name_of_swmm_half_the_two_year_out_file = return_period + scenario["condition"] + ".out"

            name_of_swmm_half_the_two_year_inp_file_path = swmm_simulation_file_path + "\\" + name_of_swmm_half_the_two_year_inp_file
            half_the_two_runoff_interface_file(two_year_interface_file_path, half_the_two_year_interface_file_path)
            create_swmm_1_2_year_inp(input_swmm_inp_file_path, name_of_swmm_half_the_two_year_inp_file_path,
                                     return_period, scenario["condition"])

            hspf_data_io.run_swmm(swmm_simulation_file_path, name_of_swmm_half_the_two_year_inp_file, name_of_swmm_half_the_two_year_rpt_file,
                                  name_of_swmm_half_the_two_year_out_file, path_to_swmm_executable)
            peak_flow_df = get_max_peak_outfall_flows(swmm_simulation_file_path, name_of_swmm_half_the_two_year_rpt_file,
                                                      name_of_swmm_half_the_two_year_out_file,
                                                      scenario["condition"], return_period)

        outfall_peaks.append(peak_flow_df)
    peak_flow_df = pd.concat(outfall_peaks, sort=False, axis=1)
    print(scenario["condition"] + "\n")
    print(peak_flow_df)
    scenario_outfall_peaks.append(peak_flow_df)


filtered_orifice_sizes = [0.375, 0.5, 0.625, 0.75, 0.875,
                 1.0, 1.125, 1.25, 1.375, 1.5, 1.625, 0.75, 0.875,
                 2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875,
                 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875]

private_orifice_sizes = [
                 1.0, 1.125, 1.25, 1.375, 1.5, 1.625, 0.75, 0.875,
                 2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875,
                 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875]

public_orifice_sizes = [
                 2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875,
                 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875]

orifice_sizes = filtered_orifice_sizes


outfalls = scenario_outfall_peaks[0].index.values
starting_area = 100
max_area = 43560

excel_output_file = swmm_simulation_file_path + "\\" + "facility_results.xlsx"

best_facility_for_outfalls = []
for outfall in outfalls:
    best_area_for_outfall = None
    predeveloped_peak_flows = scenario_outfall_peaks[0]
    developed_peak_flows = scenario_outfall_peaks[1]
    outfall_predeveloped_peak_flows = predeveloped_peak_flows.loc[outfall]
    print(outfall + "\n")
    for orifice_size in orifice_sizes:
        best_area_for_orifice_size = None
        area = starting_area
        for iteration in range(1, 1000):
            area = area + 10
            target_hit = []
            facility_outfall = "F_" + outfall
            post = 4 * [None]
            pre = 4 * [None]
            for index, return_period in enumerate(return_periods):
                target_flow = outfall_predeveloped_peak_flows.loc["predeveloped" + return_period]
                input_simulation_inp_file_path = swmm_simulation_file_path + "\\" + "facility" + outfall +  ".inp"
                name_of_swmm_rpt_file = "facility" + outfall + ".rpt"
                name_of_swmm_out_file = "facility" + outfall + ".out"
                interface_file = "developed" + return_period + "outflow.txt\n"
                update_facility_inp(input_facility_inp_file_path,
                                    input_simulation_inp_file_path,
                                    interface_file,
                                    area,
                                    orifice_size,
                                    outfall,
                                    facility_outfall)
                hspf_data_io.run_swmm(swmm_simulation_file_path, input_simulation_inp_file_path, name_of_swmm_rpt_file,
                                      name_of_swmm_out_file, path_to_swmm_executable)
                hspf_data_io.write_swmm_ini_file(swmm_simulation_file_path)
                max_flow = get_max_peak_outfall_flow_facility(swmm_simulation_file_path, name_of_swmm_rpt_file, name_of_swmm_out_file,
                                                              facility_outfall)
                if max_flow > target_flow:
                    print(outfall + " " + "  For return period: " + return_period + " Orifice:" + str(orifice_size) +
                          " Area:" + str(area) + " PeakFlow:" + str(max_flow) + " > " +
                          " TargetFlow:" + str(target_flow) + "\n")
                    post[index] = max_flow
                    pre[index] = target_flow
                    target_hit.append(False)
                    break
                else:
                    print(outfall + " " + "  For return period: " + return_period + " Orifice:" + str(orifice_size) +
                          " Area:" + str(area) + " PeakFlow:" + str(max_flow) + " <= " +
                          " TargetFlow:" + str(target_flow) + "\n")
                    post[index] = max_flow
                    pre[index] = target_flow
                    target_hit.append(True)
            if False in target_hit:
                print("  Fail *****\n")
            elif len(target_hit) == 4:
                print("  Pass *****\n")
                best_area_for_orifice_size = area
                break
        if best_area_for_outfall == None:
            best_area_for_outfall = best_area_for_orifice_size
            best_facility_for_outfall = {"outfall": outfall, "area": best_area_for_outfall, "orifice_size": orifice_size,
                                        "post 1_2 2yr": post[0], "post 5yr": post[1], "post 10yr":  post[2],  "post 25yr":  post[3],
                                        "pre 1_2 2yr": pre[0], "pre 5yr": pre[1], "pre 10yr": pre[2],  "pre 25yr": pre[3]}
        elif best_area_for_orifice_size <= best_area_for_outfall:
            best_area_for_outfall = best_area_for_orifice_size
            best_facility_for_outfall = {"outfall": outfall, "area": best_area_for_outfall, "orifice_size": orifice_size,
                            "post 1_2 2yr": post[0], "post 5yr": post[1], "post 10yr":  post[2],  "post 25yr":  post[3],
                            "pre 1_2 2yr": pre[0], "pre 5yr": pre[1], "pre 10yr": pre[2],  "pre 25yr": pre[3]}
        else:
            best_facility_for_outfalls.append(best_facility_for_outfall)
            break
facility_data_frame = pd.DataFrame(best_facility_for_outfalls)
facility_data_frame.to_excel(excel_output_file, index=False)



