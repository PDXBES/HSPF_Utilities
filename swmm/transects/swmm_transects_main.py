from swmm.transects.businessclasses.epa_swmm import Transects
from swmm.transects.businessclasses.epa_swmm import TransectsWriter
from swmm.transects.businessclasses.epa_swmm import TransectsReader
from swmm.transects.businessclasses.epa_swmm import ProjectBase
from swmm.transects.businessclasses.epa_swmm import InputFileReader
from swmm.transects.businessclasses.epa_swmm import InputFileWriterBase
from swmm.transects.dataio.transect_dataio import TransectDataIo
from swmm.transects.businessclasses.swmmtransects import SWMMTransects
import sys


def main(argv):
    copy_transects_in_input_SWMM_file_not_in_excel_input_file = True
    emgaats_model_directory = argv[0]
    simulation_swmm_inp_file_path = argv[1]
    input_SWMM_file_name = simulation_swmm_inp_file_path
    excel_input_file_path = emgaats_model_directory + r"\OpenChannel.xlsx"
    output_SWMM_file_name = simulation_swmm_inp_file_path

    transects_class = Transects()
    transects_reader = TransectsReader()
    transects_writer = TransectsWriter()

    transect_dataio = TransectDataIo()
    transect_dataio.file_path = excel_input_file_path

    swmmtransects = SWMMTransects(transect_dataio)

    transect_dataio.get_trapezoidal_transect_data_dataframe()
    transect_dataio.get_street_transect_data_dataframe()
    transect_dataio.get_natural_channel_transect_data_dataframe()
    transect_dataio.get_natural_channel_xs_transect_data_dataframe()
    transect_dataio.get_surveyed_ditch_transect_data_dataframe()
    transect_dataio.get_surveyed_ditch_xs_transect_data_dataframe()

    swmmtransects.create_street_transects()
    swmmtransects.create_trapezoid_transects()
    swmmtransects.create_irregular_ditch_transects()
    swmmtransects.create_natural_channel_transects()
    transects = swmmtransects.get_all_transects()

    # node_gdf = swmmtransects.create_irregular_ditch_nodes()
    # node_gdf.to_file(output_geopackage, layer='nodes', driver="GPKG")
    # link_gdf = swmmtransects.create_irregular_ditch_links()
    # link_gdf.to_file(output_geopackage, layer='links', driver="GPKG")

    project = ProjectBase()
    input_reader = InputFileReader()
    input_writer = InputFileWriterBase()

    # read swmm inp file
    input_reader.read_file(project, input_SWMM_file_name)

    # find the transects section
    try:
        transect_section_index = project.section_order.index('[TRANSECTS]')

        if copy_transects_in_input_SWMM_file_not_in_excel_input_file:
            # get the old transects
            old_transects = transects_reader.read(project.sections[transect_section_index].value).value
            for old_transect in old_transects:
                old_transect_updated = False
                for transect in transects:
                    if old_transect.name == transect.name:
                        old_transect_updated = True
                if not old_transect_updated:
                    transects.append(old_transect)

        transects_class.value = transects
        transects_txt = transects_writer.as_text(transects_class)

        # delete old transect section
        del project.sections[transect_section_index]

        # update transect attribute
        input_reader.read_section(project, "TRANSECTS", transects_txt)

        # add transects to project from attributes
        project.add_sections_from_attributes()

        # Transects can't be at the end of the file
        # This pops it from the end of the section list and puts it at the location of the original transect section
        project.sections.insert(transect_section_index, project.sections.pop(len(project.sections)-1))

        input_writer.write_file(project, output_SWMM_file_name)
    except:
        print("No Transects Added")


if __name__ == "__main__":
    # logfile_path = "ccsp.log"
    # logging.basicConfig(filename=logfile_path, filemode='w', level=logging.ERROR)
    main(sys.argv[1:])

