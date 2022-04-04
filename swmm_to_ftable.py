from swmmtoolbox import swmmtoolbox
import pandas as pd


def stage_storage_flow(out_file, storage_link_names, storage_node_names,
                       outfall_link_names=None, outfall_node_names=None,
                       depth_node=None):
    link_list_detail_df = swmmtoolbox.listdetail(out_file, 'link')
    node_list_detail_df = swmmtoolbox.listdetail(out_file, 'node')

    outfall_link_flows = []
    outfall_node_flows = []
    depth = None

    if storage_link_names is not None:
        link_volume = 0
        for link in link_list_detail_df.itertuples():
            link_name = link[1]
            if link_name in storage_link_names:
               link_volume += swmmtoolbox.extract(out_file, ['link', link_name, 'Froude_number']).max()[0] #values[-1][0]
            else:
                print("Link: " + link_name + " Not in storage links")
    else:
        link_volume = 0

    if outfall_link_names is not None:
        for link in link_list_detail_df.itertuples():
            link_name = link[1]
            if link_name in outfall_link_names:
                outfall_link_flows.append(swmmtoolbox.extract(out_file, ['link', link_name, 'Flow_rate']).values[-1][0])
    if len(outfall_link_flows) == 0:
        outfall_link_flows = None

    if storage_node_names is not None:
        node_volume = 0
        node_list_detail_df = swmmtoolbox.listdetail(out_file, 'node')
        for node in node_list_detail_df.itertuples():
            node_name = node[1]
            if node_name in storage_node_names:
                node_volume +=swmmtoolbox.extract(out_file, ['node', node_name, 'Volume_stored_ponded']).max()[0] #values[-1][0]
            else:
                print("Node: " + node_name + " Not in storage nodes.")
    else:
        node_volume = 0

    if outfall_node_names is not None:
        for node in node_list_detail_df.itertuples():
            node_name = node[1]
            if node_name in outfall_node_names:
                outfall_node_flows.append(swmmtoolbox.extract(out_file, ['node', node_name, "Total_inflow"]).values[-1][0])
    if len(outfall_node_flows) == 0:
        outfall_node_flows = None

    if depth_node is not None:
        for node in node_list_detail_df.itertuples():
            node_name = node[1]
            if node_name == depth_node:
                depth = swmmtoolbox.extract(out_file, ['node', node_name, "Depth_above_invert"]).values[-1][0]
    total_volume = link_volume + node_volume

    return total_volume, outfall_link_flows, outfall_node_flows, depth


def calculate_ftable_areas(ftable_df):
    start_depth = 0
    start_volume = 0
    start_area = 0
    areas = []
    for row in ftable_df.itertuples():
        end_depth = row.Depth
        end_volume = row.Volume/43560
        area = (end_volume-start_volume)/((end_depth - start_depth)/2) + start_area
        areas.append(area)
        start_depth = end_depth
        start_volume = end_volume
        start_area = area
    return areas


def write_hspf_ftable_block_text(stage_storage_flow_df_dicts):
    ftables_header = "FTABLES\n"
    ftable_number = 1
    ftables_text = ""
    for ftable_name in stage_storage_flow_df_dicts.keys():
        ftable_df = stage_storage_flow_df_dicts[ftable_name].copy(deep=True)
        columns = ftable_df.columns
        outflow_columns = [i for i in columns if i not in ('Depth', 'Volume')]
        ftable_df['Area'] = calculate_ftable_areas(ftable_df)
        number_of_rows, number_of_columns = ftable_df.shape
        ftable_row_data = list(ftable_df.itertuples(index=False))
        ftable_header = "  FTABLE   {:3d}\n".format(ftable_number)
        ftable_number_of_rows_and_columns = "{:5d}{:5d}\n".format(number_of_rows + 1, number_of_columns)
        ftable_rows_header = "     Depth      Area    Volume"
        for i in range(len(outflow_columns)):
            ftable_rows_header += "  Outflow "
        ftable_rows_header += "***\n"
        ftable_rows_header += "      (ft)   (acres) (acre-ft)"
        for i in range(len(outflow_columns)):
            ftable_rows_header += "    (cfs) "
        ftable_rows_header += "***\n"

        ftable_rows = "{:10.5f}{:10.3f}{:10.3f}".format(0, 0, 0)
        ftable_outflows = ""
        for i in range(len(outflow_columns)):
            ftable_outflows += "{:10.3f}".format(0)
        ftable_outflows += "\n"
        ftable_rows += ftable_outflows
        for row in ftable_row_data:
            ftable_rows += "{:10.5f}{:10.3f}{:10.3f}".format(row.Depth, row.Area, row.Volume/43560)
            ftable_outflows = ""
            for outflow_column in outflow_columns:
                ftable_outflows += "{:10.3f}".format(row[ftable_df.columns.get_loc(outflow_column)])
            ftable_outflows += "\n"
            ftable_rows += ftable_outflows
        ftable_footer = "  END FTABLE {:3d}\n".format(ftable_number)
        ftables_text += ftable_header + ftable_number_of_rows_and_columns + ftable_rows_header + ftable_rows + ftable_footer + "\n"
        ftable_number += 1
    ftables_footer = "END FTABLES\n"
    text = ftables_header + \
           ftables_text + \
           ftables_footer
    return text


def write_ftable_text(ftable_number, ftable_name, stage_storage_flow_df):
    pass


def create_swmm_depth_area_curve_text(stage_storage_flow_df):
    pass


def create_swmm_depth_discharge_curve_text(stage_storage_flow_df):
    pass


def create_storage_nodes_text(stage_storage_flow_df):
    pass


def write_ftable_block_to_file(filepath, stage_storage_flow_df_dicts):
    ftable_block_text = write_hspf_ftable_block_text(stage_storage_flow_df_dicts)
    with open(filepath) as ftable_file:
        ftable_file.write(ftable_block_text)


def write_swmm_depth_discharge_curves_to_file(file, stage_storage_flow_df_dicts):
    pass


def write_swmm_depth_storage_curves_to_file(file, stage_storage_flow_df_dicts):
    pass


f_dict = {}
ftable_df = pd.read_excel(r"C:\Users\sggho\Documents\HSPFModels\Models\TryonMainstemSimple\ftableout.xlsx", index_col=0)
f_dict['ftable1'] = ftable_df
text = write_hspf_ftable_block_text(f_dict)
print(text)
pass