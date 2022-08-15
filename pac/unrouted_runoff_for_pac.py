from wdmtoolbox import wdmtoolbox
import pandas as pd

start_date_time = "10/1/1977"
stop_date_time = "10/1/2021"
rgs = [3, 4, 10, 14, 153]
evap_dsn = 1
interval_in_minutes = 5
areas_in_sqft = [1000, 5000, 10000]

hru_area_in_acres = 1
number_of_intervals_after_storm_event = 1440

flow_units = "cfs"
area_units = "acre"

precip_units = "in/{} min".format(interval_in_minutes)
evap_units = "in/{} min".format(interval_in_minutes)


# suro_impervious_dsns = {'Building': (1101, area_in_acres), 'Road/Pkg Flat': (1102, area_in_acres), 'Road/Pkg Moderate': (1103, area_in_acres), 'Road/Pkg Stp': (1104, area_in_acres), 'Road/Pkg VStp': (1105, area_in_acres)}
# suro_ifwo_predeveloped_pervious_base_dsn = {
#                                             'Till Forest Flat': (10, area_in_acres),
#                                             'Till Forest Moderate': (11, area_in_acres),
#                                             'Till Forest Steep': (12, area_in_acres),
#                                             'Outwash Forest Flat': (1, area_in_acres),
#                                             'Outwash Forest Moderate': (2, area_in_acres),
#                                             'Outwash Forest Steep': (3, area_in_acres),
#                                             'Saturated Forest Flat': (19, area_in_acres),
#                                             'Saturated Forest Moderate': (20, area_in_acres),
#                                             'Saturated Forest Steep': (21, area_in_acres),
#                                             }
#suro_impervious_dicts = [{'Post': (1101, area_in_acres, 'Building')}]

def filter_df_based_on_start_and_stop_dates(df, start_date_time, stop_date_time):
    if start_date_time is not None and stop_date_time is not None:
        df = df.loc[start_date_time:stop_date_time]
    return df


def _extract_dsn_and_resample(dsn, wdm_file, output_timestep_in_minutes=None):
    flow = wdmtoolbox.extract(wdm_file, dsn).fillna(value=0)
    if output_timestep_in_minutes is not None:
        flow = flow.resample(str(output_timestep_in_minutes) + 'T').mean()
    return flow


def create_hru_surface_flow_dataframe(wdm_file, surface_flow_dsns, start_date_time, stop_date_time):
    dsns = surface_flow_dsns.values()
    dsn_names = surface_flow_dsns.keys()
    hru_surface_flows = []
    for name, dsn_and_area in zip(dsn_names, dsns):
        dsn = dsn_and_area[0]
        flow = _extract_dsn_and_resample(dsn, wdm_file)
        flow = filter_df_based_on_start_and_stop_dates(flow, start_date_time, stop_date_time)
        flow = flow.rename(columns={flow.columns[0]: name})
        flow[name] = flow[name] * area_in_acres/hru_area_in_acres
        hru_surface_flows.append(flow)
    hru_surface_flow_df = pd.concat(hru_surface_flows, axis=1)
    return hru_surface_flow_df


def create_hru_pervious_flow_dataframe(wdm_file, suro_ifwo_predeveloped_pervious_base_dsn, start_date_time, stop_date_time):
    dsns = suro_ifwo_predeveloped_pervious_base_dsn.values()
    dsn_names = suro_ifwo_predeveloped_pervious_base_dsn.keys()
    hru_pervious_flows = []
    for name, dsn_and_area in zip(dsn_names, dsns):
        dsn = dsn_and_area[0]
        suro_dsn = dsn + 1000
        suro_flow = _extract_dsn_and_resample(suro_dsn, wdm_file)
        suro_flow = filter_df_based_on_start_and_stop_dates(suro_flow, start_date_time, stop_date_time)
        suro_flow = suro_flow.rename(columns={suro_flow.columns[0]: name})

        ifwo_dsn = dsn + 3000
        ifwo_flow = _extract_dsn_and_resample(ifwo_dsn, wdm_file)
        ifwo_flow = filter_df_based_on_start_and_stop_dates(ifwo_flow, start_date_time, stop_date_time)
        ifwo_flow = ifwo_flow.rename(columns={ifwo_flow.columns[0]: name})
        pervious_flow = suro_flow[name].add(ifwo_flow[name]).to_frame()
        pervious_flow = pervious_flow.rename(columns={ifwo_flow.columns[0]: name})
        pervious_flow[name] = pervious_flow[name] * area_in_acres/hru_area_in_acres
        hru_pervious_flows.append(pervious_flow)

    hru_surface_flow_df = pd.concat(hru_pervious_flows, axis=1)
    return hru_surface_flow_df

for area_in_sqft in areas_in_sqft:
    area_in_acres = area_in_sqft / 43560
    suro_ifwo_predeveloped_pervious_dicts = [{'Pre': (10, area_in_acres, 'Forest Flat C', 'Tryon W')},
                                             {'Pre': (11, area_in_acres, 'Forest Mod C', 'Tryon W')},
                                             {'Pre': (12, area_in_acres, 'Forest Stp C', 'Tryon W')},

                                             {'Pre': (110, area_in_acres, 'Forest Flat C', 'Tryon S')},
                                             {'Pre': (111, area_in_acres, 'Forest Mod C', 'Tryon S')},
                                             {'Pre': (112, area_in_acres, 'Forest Stp C', 'Tryon S')},

                                             {'Pre': (410, area_in_acres, 'Forest Flat C', 'Tryon NE')},
                                             {'Pre': (411, area_in_acres, 'Forest Mod C', 'Tryon NE')},
                                             {'Pre': (412, area_in_acres, 'Forest Stp C', 'Tryon NE')},

                                             {'Pre': (210, area_in_acres, 'Forest Flat C', 'Western Washington Regional Parameters')},
                                             {'Pre': (211, area_in_acres, 'Forest Mod C', 'Western Washington Regional Parameters')},
                                             {'Pre': (212, area_in_acres, 'Forest Stp C', 'Western Washington Regional Parameters')},

                                             {'Pre': (310, area_in_acres, 'Forest Flat C', 'TRUST')},
                                             {'Pre': (311, area_in_acres, 'Forest Mod C', 'TRUST')},
                                             {'Pre': (312, area_in_acres, 'Forest Stp C', 'TRUST')}
                                             ]
    suro_impervious_dicts = len(suro_ifwo_predeveloped_pervious_dicts)*[{'Post': (2001, area_in_acres, 'Building')}]
    for rg_dsn in rgs:
        for suro_impervious_dict, suro_ifwo_predeveloped_pervious_dict in zip(suro_impervious_dicts, suro_ifwo_predeveloped_pervious_dicts):
            post_column_name = list(suro_impervious_dict.keys())[0]
            pre_column_name = list(suro_ifwo_predeveloped_pervious_dict.keys())[0]
            post_dsn = list(suro_impervious_dict.values())[0][0]
            pre_dsn = list(suro_ifwo_predeveloped_pervious_dict.values())[0][0]
            pre_description = list(suro_ifwo_predeveloped_pervious_dict.values())[0][2] + " " + list(suro_ifwo_predeveloped_pervious_dict.values())[0][3] + " " + str(pre_dsn)
            post_description = list(suro_impervious_dict.values())[0][2] + " " + str(post_dsn)
            sim = r"\\BESFile1\ASM_Projects\PACHSPFRunoff\Models\TryonParameters\sim"
            simulation_folder = sim + "\\" + "TryonCreekParameters_EXISTING_RG{}".format(rg_dsn)
            output_file_name = "{}sqft_Pre_{}_Post_{}_RG{}_output_wy_1978_to_wy_2021".format(area_in_sqft, pre_description, post_description, rg_dsn)
            description = "Area in sq ft:" + str(area_in_sqft) + str() + " Pre:" + pre_description + " Post:" + post_description + " RG{}".format(rg_dsn)
            met_data_wdm_file_name = r"Met5min.wdm"
            evap_data_wdm_file_name = r"Evap5min.wdm"
            met_data_wdm_file = simulation_folder + "\\" + met_data_wdm_file_name
            evap_data_wdm_file = sim + "\\" + evap_data_wdm_file_name
            unrouted_flow_data_wdm_file = simulation_folder + "\\" + "hru" + str(rg_dsn) + ".wdm"
            output_csv_file = r"\\BESFile1\ASM_Projects\PACHSPFRunoff\Models\TryonParameters\sim\runoff" + "\\" + "" + output_file_name + ".txt"

            precip = _extract_dsn_and_resample(rg_dsn, met_data_wdm_file, output_timestep_in_minutes=5)
            precip = filter_df_based_on_start_and_stop_dates(precip, start_date_time, stop_date_time)
            precip = precip.rename(columns={precip.columns[0]: 'Precip'})

            evap = _extract_dsn_and_resample(evap_dsn, evap_data_wdm_file, output_timestep_in_minutes=5)
            evap = filter_df_based_on_start_and_stop_dates(evap, start_date_time, stop_date_time)
            evap = evap.rename(columns={evap.columns[0]: 'Evap'})

            pervious_flow_df = create_hru_pervious_flow_dataframe(unrouted_flow_data_wdm_file, suro_ifwo_predeveloped_pervious_dict, start_date_time, stop_date_time)
            impervious_flow_df = create_hru_surface_flow_dataframe(unrouted_flow_data_wdm_file, suro_impervious_dict, start_date_time, stop_date_time)
            #flow_df = create_hru_surface_flow_dataframe(unrouted_flow_data_wdm_file, suro_impervious_dsns, start_date_time, stop_date_time)
            met_and_flow_df = pd.concat([precip, evap, impervious_flow_df, pervious_flow_df], axis=1)

            start_date = pd.to_datetime(met_and_flow_df.index.values[0]).strftime("%Y-%m-%dT%H:%M:%S-08:00")

            #columns = ['Precip', 'Evap'] + [post_column_name, pre_column_name]
            with open(output_csv_file, 'w') as out:
                # out.write(description + '\r')
                # out.write(precip_units + '\r')
                # out.write(evap_units + '\r')
                # out.write(flow_units + '\r')
                # out.write(str(area_in_acres) + " " + area_units + '\r')
                # out.write(start_date + '\r')
                out.write(str(interval_in_minutes) + '\r')
                out.write(str(number_of_intervals_after_storm_event) + '\r')
                out.write(start_date + '\r')
            met_and_flow_df.to_csv(output_csv_file, columns=['Post', 'Pre'], index=False, float_format='%.8f', header=False,
                                   line_terminator='\r\n', mode='a', sep=',')
        # met_and_flow_df.to_csv(output_csv_file, columns=['Post', 'Pre'], index=False, float_format='%.4e', header=False,
        #                            line_terminator='\r\n', mode='a', sep=',')

# with open(output_csv_file, 'w') as out:
#     #out.write(description +"\r")
#     out.write(flow_units + '\r')
#     out.write(start_date + '\r')
#     out.write(str(interval_in_minutes) + '\r')
#     out.write(str(number_of_intervals_after_storm_event) + '\r')
# columns = ['Precip', 'Evap'] + list(suro_impervious_dsns.keys()) + list(suro_ifwo_predeveloped_pervious_base_dsn.keys())
# met_and_flow_df.to_csv(output_csv_file, columns=columns, index=False, float_format='%.8f', header=True, line_terminator='\r\n', mode='a', sep=',')