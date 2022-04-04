import pandas as pd
import sys


def main(argv):
    emgaats_model_directory = argv[0]
    simulation_swmm_inp_file_path = argv[1]
    excel_input_file_path = emgaats_model_directory + r"\OpenChannel.xlsx"
    output_swmm_file_name = simulation_swmm_inp_file_path

    section_header ="[LOSSES]\n"
    losses_header = ";;Link          \tKentry    \tKexit     \tKavg      \tFlap Gate \tSeepage   \n" +\
                    ";;--------------\t----------\t----------\t----------\t----------\t----------\n"

    loss_format = "{:16}\t{:10}\t{:10}\t{:10}\t{:10}\t{:10}\n"

    # Read data from excel into pandas dataframe
    losses_df = pd.read_excel(excel_input_file_path, sheet_name='Losses')
    # Convert dataframe to itertuples, essentially a list of order dicts, one ordered dict per row
    losses_data = losses_df.itertuples()

    loss_section_as_text = section_header
    loss_section_as_text += losses_header

    # Loop through each row in losses_data
    for loss_data in losses_data:
        loss_coefficient = 0
        flap_gate = "NO"
        seepage = 0

        # ConduitName, EntryLossCoefficient, ExitLossCoefficient column headers in excel worksheet
        # Creates string for one row
        loss_row = loss_format.format(
            loss_data.ConduitName,
            loss_data.EntryLossCoefficient,
            loss_data.ExitLossCoefficient,
            loss_coefficient,
            flap_gate,
            seepage)
        # adds string to section_text
        loss_section_as_text += loss_row

    with open(output_swmm_file_name, 'a') as out:
        out.write(loss_section_as_text)

if __name__ == "__main__":
    # logfile_path = "ccsp.log"
    # logging.basicConfig(filename=logfile_path, filemode='w', level=logging.ERROR)
    main(sys.argv[1:])