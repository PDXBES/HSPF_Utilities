from hspf.businessclasses.hspf import Hspf
from hspf.businessclasses.implnd import Implnd
from hspf.businessclasses.perlnd import Perlnd
from hspf.businessclasses.subbasin import Subbasin
from common.conversion_constants import ConversionConstants
from typing import List
try:
    from wdmtoolbox import wdmtoolbox
except:
    pass
import datetime
import shutil
import subprocess
import os
import pandas as pd


class HspfDataIo(object):
    def __init__(self, input_file):
        self.input_file = input_file
        self.conversion_constants = ConversionConstants()
        self.perlnd_suro_to_rchres_masslink = 2  # TODO move to appsettings
        self.perlnd_ifwo_to_rchres_masslink = 3  # TODO move to appsettings
        self.perlnd_agwo_to_rchres_masslink = 4  # TODO move to appsettings
        self.implnd_suro_to_rchres_masslink = 5  # TODO move to appsettings
        self.perlnd_suro_to_copy_masslink = 12  # TODO move to appsettings
        self.perlnd_ifwo_to_copy_masslink = 13  # TODO move to appsettings
        self.perlnd_agwo_to_copy_masslink = 14  # TODO move to appsettings
        self.implnd_suro_to_copy_masslink = 15  # TODO move to appsettings

    def write_hdf5_file(self, hspf: Hspf, interface_file):
        reorder_df = hspf.create_flow_df_for_interface_file()
        reorder_df.to_hdf(interface_file + ".h5", mode='w', key='df')

    def write_interface_file_header(self,  hspf: Hspf):
        number_of_nodes = len(hspf.node_outlets)
        header = "SWMM5 Interface File\n"
        header = header + "Unrouted HSPF Flows\n"
        header = header + str(hspf.output_timestep_in_minutes * self.conversion_constants.seconds_in_minute) + "\n"
        header = header + "1\n"
        header = header + "FLOW CFS\n"
        header = header + str(number_of_nodes) + "\n"
        for node in hspf.node_outlets:
            header = header + node.name + "\n"
        header = header + "Node             Year Mon Day Hr  Min Sec FLOW\n"
        return header

    def write_icm_inflow_event_file_header(self, hspf: Hspf, begin_date):
        number_of_nodes = len(hspf.node_outlets)
        header = "!Version=1,type=QIN, encoding=MBCS\n"
        header += "FILECONT, TITLE\n"
        header += "UserSettings,U_VALUES,U_DATETIME\n"
        header += "2,1\n"
        header += "UserSettingsValues, ft3/s, mm-dd-yyyy hh:mm\n"
        header += "G_START,G_TS,G_NPROFILES,G_DATATYPE\n"
        header += begin_date + "," + "300" + "," + str(number_of_nodes) + ", 0\n"
        header += "L_NODEID,L_PTITLE\n"
        for node in hspf.node_outlets:
            header += node.name + ",\n"
        header += "P_DATETIME,"
        for node in hspf.node_outlets:
            header += node.name + ","
        header += "\n"
        return header

    def write_icm_inflow_event_file(self, hspf: Hspf, icm_file_path, begin_date, end_date):
        df = hspf.flow_in_columns_df.loc[begin_date: end_date]
        with open(icm_file_path, 'w') as f:
            header = self.write_icm_inflow_event_file_header(hspf, begin_date)
            f.write(header)
        df.to_csv(icm_file_path, header=False, mode='a', date_format='%mm/%dd/%Y %H:%M:%s', float_format='%.8f')

    def write_xpx_file(self, hspf: Hspf, xpx_file_path, begin_date, end_date):
        df = hspf.flow_in_columns_df.loc[begin_date: end_date]
        df["dt"] = df.index.values
        t0 = min(df['dt'].values)
        df['hour'] = df['dt'].apply(lambda x: (x - t0).days * 24 + (x - t0).seconds / 3600.0)
        df = df.round(8)
        hours = df['hour'].values
        ct = len(hours)
        hours_list = ' '.join(['{:.8f}'.format(x) for x in hours])
        with open(xpx_file_path, 'w') as o:
            for fld in df.columns:
                if fld in ['dt', 'hour']:
                    pass
                else:
                    values = df[fld].values
                    values = ' '.join(['{:.8f}'.format(x) for x in values])

                    o.write('DATA INQ "%s" 0 1 1\n' % fld)
                    o.write('DATA TEO "%s" 0 %s %s\n' % (fld, ct, hours_list))
                    o.write('DATA QCARD "%s" 0 %s %s\n' % (fld, ct, values))

    def write_interface_file(self, hspf: Hspf, interface_file):
        reorder_df = hspf.create_flow_df_for_interface_file()

        flattened_reorder_df = reorder_df.to_numpy().flatten()
        with open(interface_file, 'w') as f:
            header = self.write_interface_file_header(hspf)
            f.write(header)
            print("Total Volume Rounded:" + " " + str(reorder_df['Flow'].round(15).sum() * hspf.input_timestep_in_minutes * 60 /43560))
            print("Total Volume Flow:" + " " + str(reorder_df['Flow'].sum() * hspf.input_timestep_in_minutes * 60 /43560))
            #TODO does swmm understand scientific notation does 8 versus 15 decemal places matter
            fmt = ''.join(['%6s %19s %.15f\n'] * len(reorder_df.index))
            data = fmt % tuple(flattened_reorder_df)
            f.write(data)
        pass

    def write_interface_file_half_flow(self, hspf: Hspf, interface_file):
        reorder_df = hspf.create_flow_df_for_interface_file_half_flow()

        flattened_reorder_df = reorder_df.to_numpy().flatten()
        with open(interface_file, 'w') as f:
            header = self.write_interface_file_header(hspf)
            f.write(header)
            print("Total Volume Rounded:" + " " + str(reorder_df['Flow'].round(15).sum() * hspf.input_timestep_in_minutes * 60 /43560))
            print("Total Volume Flow:" + " " + str(reorder_df['Flow'].sum() * hspf.input_timestep_in_minutes * 60 /43560))
            fmt = ''.join(['%6s %19s %.15f\n'] * len(reorder_df.index))
            data = fmt % tuple(flattened_reorder_df)
            f.write(data)
        pass

    def write_interface_file_for_ftable_creation(self, hspf: Hspf, interface_file, factor=1):
        reorder_df = hspf.create_flow_df_for_interface_file_for_ftable_creation()
        reorder_df['Flow'] = reorder_df['Flow'] * factor
        flattened_reorder_df = reorder_df.to_numpy().flatten()
        with open(interface_file, 'w') as f:
            header = self.write_interface_file_header(hspf)
            f.write(header)
            fmt = ''.join(['%6s %19s %f\n'] * len(reorder_df.index))
            data = fmt % tuple(flattened_reorder_df)
            f.write(data)

    def write_subbasins_summary_file(self, hspf: Hspf, subbasin_summary_file):
        with open(subbasin_summary_file, 'w') as summary_file:
            for subbasin in hspf.subbasins:
                if subbasin.emgaats_area > 0:
                    summary_file.write(str(subbasin.subbasin_name) + "\n")
                    summary_file.write("Overlay area: " + str(subbasin.total_area) + " EMGAATS area:" +str(subbasin.emgaats_area) + "\n")
                    summary_file.write("%difference: " + str(round(((subbasin.total_area - subbasin.emgaats_area)/subbasin.emgaats_area), )) + "\n")
                    summary_file.write(str(subbasin.total_area) + "\n")
                    summary_file.write(str(subbasin.total_pervious_area) + "\n")
                    summary_file.write(str(subbasin.total_impervious_area) + "\n")
                    summary_file.write(str(subbasin.total_effective_impervious_area) + "\n")
                    summary_file.write("\n")
            for subbasin in hspf.explicit_impervious_area_subbasins:
                if subbasin.emgaats_area > 0:
                    summary_file.write(str(subbasin.subbasin_name) + "\n")
                    summary_file.write("Overlay area: " + str(subbasin.total_area) + " EMGAATS area:" +str(subbasin.emgaats_area) + "\n")
                    summary_file.write("%difference: " + str(round(((subbasin.total_area - subbasin.emgaats_area)/subbasin.emgaats_area), )) + "\n")
                    summary_file.write(str(subbasin.total_area) + "\n")
                    summary_file.write(str(subbasin.total_pervious_area) + "\n")
                    summary_file.write(str(subbasin.total_impervious_area) + "\n")
                    summary_file.write(str(subbasin.total_effective_impervious_area) + "\n")
                    summary_file.write("\n")

    def write_hspf_schematic_block_to_file(self, subbasins: List[Subbasin], hspf: Hspf, hspf_perlnd_implnd_file):
        with open(hspf_perlnd_implnd_file, 'w') as perlnd_implnd_file:
            text = self.write_hspf_schematic_block_text(hspf, subbasins)
            perlnd_implnd_file.write(text)

    def write_hspf_hru_uci_to_file(self, hspf, hspf_uci_file, description, rg, start_date, stop_date, rg_multiplier, evap_dsn, evap_multiplier):
        hru = True
        with open(hspf_uci_file, 'w') as uci_file:
            text = \
                "RUN\n" + \
                self.write_hspf_global_as_text(description, start_date, stop_date) + "\n" + \
                self.write_hspf_files_as_text(rg, hru) + "\n" + \
                self.write_hspf_open_sequence_as_text(hspf, hru) + "\n" + \
                self.write_hspf_copy_block_text() + "\n" + \
                self.write_hspf_perlnd_block_text(hspf) + "\n" + \
                self.write_hspf_implnd_block_text(hspf) + "\n" + \
                self.write_hspf_hru_schematic_block_text(hspf) + "\n" + \
                self.write_hspf_ext_sources_as_text_multiple_rgs(rg, rg_multiplier, evap_dsn, evap_multiplier, hru) + "\n" + \
                self.write_hspf_hru_ext_targets_as_text(hspf) + "\n" + \
                self.write_hspf_mass_link_as_text() + \
                "END RUN\n"
            uci_file.write(text)

    def write_hspf_design_storm_hru_uci_to_file(self, hspf, hspf_uci_file, description, storm, start_date, stop_date, rg_multiplier, evap, evap_multiplier, predevelopment=False):
        hru = True
        with open(hspf_uci_file, 'w') as uci_file:
            if predevelopment:
                storms = {'PreD25yr24hrSCS': 2025,  # TODO should be enumeration
                          'PreD10yr24hrSCS': 2010,
                          'PreWQ': 2000,
                          'Pre1_2_D02yr24hrSCS': 2002,
                          'PreD02yr24hrSCS': 2002,
                          'PreD05yr24hrSCS': 2005,
                          'PreD100yr24hrSCS': 2100
                          }
            else:
                storms = {'D25yr24hrSCS': 2025,  # TODO should be enumeration
                          'D10yr24hrSCS': 2010,
                          'WQ': 2000,
                          '1_2_D02yr24hrSCS': 2002,
                          'D02yr24hrSCS': 2002,
                          'D05yr24hrSCS': 2005,
                          'D100yr24hrSCS': 2100
                          }
            text = \
                "RUN\n" + \
                self.write_hspf_global_as_text(description, start_date, stop_date) + "\n" + \
                self.write_hspf_files_design_storm_as_text(storm) + "\n" + \
                self.write_hspf_open_sequence_as_text(hspf, hru) + "\n" + \
                self.write_hspf_copy_block_text() + "\n" + \
                self.write_hspf_perlnd_block_text(hspf) + "\n" + \
                self.write_hspf_implnd_block_text(hspf) + "\n" + \
                self.write_hspf_hru_schematic_block_text(hspf) + "\n" + \
                self.write_hspf_ext_sources_as_text(storms[storm], rg_multiplier, evap, evap_multiplier, hru) + "\n" + \
                self.write_hspf_hru_ext_targets_as_text(hspf) + "\n" + \
                self.write_hspf_mass_link_as_text() + \
                "END RUN\n"
            uci_file.write(text)

    def write_hspf_uci_to_file(self, hspf, hspf_uci_file, name, description, rg, start_date, stop_date, rg_multiplier,evap, evap_multiplier):
        hru = False
        with open(hspf_uci_file, 'w') as uci_file:
            text = \
                "RUN\n" + \
                self.write_hspf_global_as_text(description, start_date, stop_date) + "\n" + \
                self.write_hspf_files_as_text(rg, hru) + "\n" + \
                self.write_hspf_open_sequence_as_text(hspf, hru) + "\n" + \
                self.write_hspf_dss_path_names_block_as_text(rg, name) + "\n" + \
                self.write_hspf_copy_block_text() + "\n" + \
                self.write_hspf_perlnd_block_text(hspf) + "\n" + \
                self.write_hspf_implnd_block_text(hspf) + "\n" + \
                self.write_hspf_rchres_block_text() + "\n" + \
                self.write_hspf_ftable_block_text(hspf) + "\n" +\
                self.write_hspf_schematic_block_text(hspf, hspf.subbasins + hspf.explicit_impervious_area_subbasins) + "\n" + \
                self.write_hspf_ext_sources_as_text(rg, rg_multiplier, evap, evap_multiplier, hru) + "\n" + \
                self.write_hspf_ext_targets_as_text() + "\n" + \
                self.write_hspf_mass_link_as_text() + \
                "END RUN\n"
            uci_file.write(text)

    def write_hspf_rchres_block_text(self):
        rchres_header = "RCHRES\n"

        geninfo_header = "  GEN-INFO\n"\
                         "    RCHRES       Name        Nexits   Unit Systems   Printer                 ***\n" + \
                         "    # -  #<------------------><---> User T-series  Engl Metr LKFG            ***\n" + \
                         "                                           in  out                           ***\n"
        geninfo = "    1     Channel  1              1    1    0    0        0    0\n"
        geninfo_footer = "  END GEN-INFO\n"

        activity_header = "  ACTIVITY\n"\
                          "    <PLS > ************* Active Sections *****************************\n" + \
                          "    # -  # HYFG ADFG CNFG HTFG SDFG GQFG OXFG NUFG PKFG PHFG ***\n"
        activity = "    1  999    1    0    0    0    0    0    0    0    0    0\n"
        activity_footer = "  END ACTIVITY\n"

        hyd_parm1_header = "  HYDR-PARM1\n" +\
            "    RCHRES  Flags for each HYDR Section                                      ***\n" +\
            "    # -  #  VC A1 A2 A3  ODFVFG for each *** ODGTFG for each     FUNCT  for each\n" +\
            "            FG FG FG FG  possible  exit  *** possible  exit      possible  exit\n"
        hyd_parm1 = "    1        0  1  0  0    4  0  0  0  0       0  0  0  0  0       2  2  2  2  2\n"
        hyd_parm1_footer = "  END HYDR-PARM1\n"

        hyd_parm2_header = "  HYDR-PARM2\n" +\
            "    # -  #    FTABNO       LEN     DELTH     STCOR        KS      DB50       ***\n" +\
            "  <------><--------><--------><--------><--------><--------><-------->       ***\n"
        hyd_parm2 = "    1              1      1.00       0.0       0.0       0.3       0.0\n"
        hyd_parm2_footer = "  END HYDR-PARM2\n"

        hydr_init_header = "  HYDR-INIT\n" +\
            "    RCHRES  Initial conditions for each HYDR section                         ***\n" +\
            "    # -  # ***   VOL     Initial  value  of COLIND     Initial  value  of OUTDGT\n" +\
            "          *** ac-ft     for each possible exit        for each possible exit\n" +\
            "  <------><-------->     <---><---><---><---><---> *** <---><---><---><---><--->\n"
        hydr_init = "    1            0         4.0  0.0  0.0  0.0  0.0       0.0  0.0  0.0  0.0  0.0\n"
        hydr_init_footer = "  END HYDR-INIT\n"

        rchres_footer = "END RCHRES\n"

        text = rchres_header + \
            geninfo_header + geninfo + geninfo_footer + "\n" +\
            activity_header + activity + activity_footer + "\n" +\
            hyd_parm1_header + hyd_parm1 + hyd_parm1_footer + "\n" +\
            hyd_parm2_header + hyd_parm2 + hyd_parm2_footer + "\n" +\
            hydr_init_header + hydr_init + hydr_init_footer + "\n" +\
            rchres_footer
        return text

    def write_hspf_ftable_block_text(self, hspf):
        ftable_row_data = list(hspf.ftable.itertuples())
        number_of_rows = len(ftable_row_data)
        number_of_columns = 4

        ftables_header = "FTABLES\n"
        ftable_header = "  FTABLE      1\n"
        ftable_number_of_rows_and_columns = "{:5d}{:5d}\n".format(number_of_rows, number_of_columns)
        ftable_rows_header = "     Depth      Area    Volume  Outflow1***\n" +\
                             "      (ft)   (acres) (acre-ft)   (cfs)  ***\n"

        ftable_rows = ""
        for row in ftable_row_data:
            ftable_rows += "{:10.3f}{:10.3f}{:10.3f}{:10.3f}\n".format(row.Depth, row.Area, row.Volume, row.Outflow1)

        ftable_footer = "  END FTABLE 1\n"
        ftables_footer = "END FTABLES\n"
        text = ftables_header + \
               ftable_header + ftable_number_of_rows_and_columns + ftable_rows_header + ftable_rows + ftable_footer +\
               ftables_footer
        return text

    def write_hspf_global_as_text(self, description, start_date, end_date):
        header = \
        "GLOBAL\n"
        description = "  " + description + "\n"
        start_end = "  START       " + start_date + "        END    " + end_date + "\n"
        run_interp = "  RUN INTERP OUTPUT LEVEL    3    0\n"
        resume = "  RESUME     0 RUN     1                   UNIT SYSTEM     1\n"
        footer = "END GLOBAL\n"
        text = header + description + start_end + run_interp + resume + footer
        return text

    def write_hspf_files_as_text(self, rg, hru):
        header = \
            "FILES\n" +\
            "<File>  <Un#>   <-----------File Name------------------------------>***\n" +\
            "<-ID->                                                              ***\n"
        if hru:
            files = \
                "WDM1       26   Met5min.wdm\n" + \
                "WDM2       37   HRU" + "SURO" + ".wdm\n" + \
                "WDM3       47   HRU" + "IFWO" + ".wdm\n" + \
                "WDM4       57   HRU" + "AGWO" + ".wdm\n" + \
                "MESSU      25   Unrouted.MES\n\n"
        else:
            files = \
                "WDM1       26   Met5min.wdm\n" + \
                "DSS1       31   Lumped" + str(rg) + ".DSS\n" + \
                "WDM2       37   Lumped" + str(rg) + ".wdm\n" + \
                "MESSU      25   Routed.MES\n\n"
        footer = "END FILES\n"
        text = header + files + footer
        return text

    def write_hspf_files_design_storm_as_text(self, storm):
        header = \
            "FILES\n" +\
            "<File>  <Un#>   <-----------File Name------------------------------>***\n" +\
            "<-ID->                                                              ***\n"
        files = \
                "WDM1       26   DesignStorm5min.wdm\n" + \
                "WDM2       37   HRU" + "SURO" + ".wdm\n" + \
                "WDM3       47   HRU" + "IFWO" + ".wdm\n" + \
                "WDM4       57   HRU" + "AGWO" + ".wdm\n" + \
                "MESSU      25   Unrouted.MES\n\n"

        footer = "END FILES\n"
        text = header + files + footer
        return text

    def write_hspf_open_sequence_as_text(self, hspf, hru):
        header = \
            "OPN SEQUENCE\n" +\
            "    INGRP              INDELT 00:05\n"

        footer = \
            "    END INGRP\n" +\
            "END OPN SEQUENCE\n"

        perlnd_string = ""
        perlnd_copy_string = ""
        for perlnd in hspf.perlnds:
            perlnd_string += "{:6s}PERLND{:5s}{:3d}\n".format(' ', ' ', perlnd.perlnd_id)
            perlnd_copy_string += "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', perlnd.perlnd_id)

        implnd_string = ""
        implnd_copy_string = ""
        for implnd in hspf.implnds:
            implnd_string += "{:6s}IMPLND{:5s}{:3d}\n".format(' ', ' ', implnd.implnd_id)
            implnd_copy_string += "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', implnd.implnd_id + 500)

        rchres_string = "{:6s}RCHRES{:5s}{:3d}\n".format(' ', ' ', 1)

        unrouted_copy_string = "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', 11)
        unrouted_copy_string += "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', 12)
        unrouted_copy_string += "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', 13)
        unrouted_copy_string += "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', 14)
        precip_copy_string = "{:6s}COPY{:7s}{:3d}\n".format(' ', ' ', 15)

        if hru:
            text = header + perlnd_string + implnd_string + perlnd_copy_string + implnd_copy_string + footer
        else:
            text = header + perlnd_string + implnd_string + unrouted_copy_string + precip_copy_string + rchres_string + footer
        return text

    def write_hspf_copy_block_text(self):
        text =\
        "COPY\n" +\
        "  TIMESERIES\n" +\
        "    # -  #  NPT  NMN ***\n" +\
        "    1  999    1    3\n" +\
        "  END TIMESERIES\n" +\
        "END COPY\n"
        return text

    def write_hspf_perlnd_block_text(self, hspf):
        header = "PERLND\n"
        gen_info = self.write_hspf_perlnd_gen_info_text(hspf) + "\n"
        activity = self.write_hspf_perlnd_activity_text() + "\n"
        pwat_parm1 = self.write_hspf_perlnd_pwat_parm1_text() + "\n"
        pwat_parm2 = self.write_hspf_perlnd_pwat_parm2_text(hspf) + "\n"
        pwat_parm3 = self.write_hspf_perlnd_pwat_parm3_text(hspf) + "\n"
        pwat_parm4 = self.write_hspf_perlnd_pwat_parm4_text(hspf) + "\n"
        pwat_state1 = self.write_hspf_perlnd_pwat_state1_text(hspf) + "\n"
        footer = "END PERLND\n"
        text = header + gen_info + activity + pwat_parm1 + pwat_parm2 + pwat_parm3 + pwat_parm4 + pwat_state1 + footer
        return text

    def write_hspf_perlnd_gen_info_text(self, hspf):
        header = \
            "  GEN-INFO\n" +\
            "    <PLS ><-------Name------->NBLKS   Unit-systems   Printer ***\n" +\
            "    # -  #                          User  t-series Engl Metr ***\n" +\
            "                                           in  out           ***\n"
        gen_info = ""
        for perlnd in hspf.perlnds:
            gen_info += "{:2s}{:3d}{:5s}{:24s}{:1d}{:5d}{:5d}{:5d}{:10d}\n".format(' ', perlnd.perlnd_id, ' ', perlnd.desc, 1, 1, 0, 0, 0)

        footer = "  END GEN-INFO\n"
        text = header + gen_info + footer
        return text

    def write_hspf_perlnd_activity_text(self):
        header = \
            "  ACTIVITY\n" +\
            "    <PLS > ************* Active Sections *****************************\n" +\
            "    # -  # ATMP SNOW PWAT  SED  PST  PWG PQAL MSTL PEST NITR PHOS TRAC ***\n"

        activity =\
            "    1  999    0    0    1    0    0    0    0    0    0    0    0    0  \n"
        footer = "  END ACTIVITY\n"
        text = header + activity + footer
        return text

    def write_hspf_perlnd_pwat_parm1_text(self):
        header = \
            "  PWAT-PARM1\n" + \
            "    <PLS >  PWATER variable monthly parameter value flags  ***\n" + \
            "    # -  # CSNO RTOP UZFG  VCS  VUZ  VNN VIFW VIRC  VLE INFC  HWT ***\n"
        pwat_parm1 = "    1  999    0    0    0    0    0    0    0    0    0    0    0 \n"
        footer = "  END PWAT-PARM1\n"
        text = header + pwat_parm1 + footer
        return text

    def write_hspf_perlnd_pwat_parm2_text(self, hspf):
        header = \
            "  PWAT-PARM2\n" + \
            "    <PLS >      PWATER input info: Part 2         ***\n" + \
            "    # -  # ***FOREST      LZSN    INFILT      LSUR     SLSUR     KVARY     AGWRC\n"
        pwater_data = hspf.pwater.itertuples()
        pwat_parm2 = ""
        for pwater in pwater_data:
            pwat_parm2 += "{:2s}{:3d}{:5s}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}\n".format(' ',
                                                                                               pwater.Number,
                                                                                               ' ',
                                                                                               pwater.FOREST,
                                                                                               pwater.LZSN,
                                                                                               pwater.INFILT,
                                                                                               pwater.LSUR,
                                                                                               pwater.SLSUR,
                                                                                               pwater.KVARY,
                                                                                               pwater.AGWRC)
        footer = "  END PWAT-PARM2\n"
        text = header + pwat_parm2 + footer
        return text

    def write_hspf_perlnd_pwat_parm3_text(self, hspf):
        header = \
            "  PWAT-PARM3\n" + \
            "    <PLS >      PWATER input info: Part 3         ***\n" + \
            "    # -  # ***PETMAX    PETMIN    INFEXP    INFILD    DEEPFR    BASETP    AGWETP\n"
        pwater_data = hspf.pwater.itertuples()
        pwat_parm3 = ""
        for pwater in pwater_data:
            pwat_parm3 += "{:2s}{:3d}{:5s}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}\n".format(' ',
                                                                                               pwater.Number,
                                                                                               ' ',
                                                                                               pwater.PETMAX,
                                                                                               pwater.PETMIN,
                                                                                               pwater.INFEXP,
                                                                                               pwater.INFILD,
                                                                                               pwater.DEEPFR,
                                                                                               pwater.BASETP,
                                                                                               pwater.AGWETP)
        footer = "  END PWAT-PARM3\n"
        text = header + pwat_parm3 + footer
        return text

    def write_hspf_perlnd_pwat_parm4_text(self, hspf):
        header = \
            "  PWAT-PARM4\n" + \
            "    <PLS >     PWATER input info: Part 4                               ***\n" + \
            "    # -  #     CEPSC      UZSN      NSUR     INTFW       IRC     LZETP ***\n"
        pwater_data = hspf.pwater.itertuples()
        pwat_parm4 = ""
        for pwater in pwater_data:
            pwat_parm4 += "{:2s}{:3d}{:5s}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}\n".format(' ',
                                                                                               pwater.Number,
                                                                                               ' ',
                                                                                               pwater.CEPSC,
                                                                                               pwater.UZSN,
                                                                                               pwater.NSUR,
                                                                                               pwater.INTFW,
                                                                                               pwater.IRC,
                                                                                               pwater.LZETP)
        footer = "  END PWAT-PARM4\n"
        text = header + pwat_parm4 + footer
        return text

    def write_hspf_perlnd_pwat_state1_text(self, hspf):
        header = \
            "  PWAT-STATE1\n" + \
            "    <PLS > *** Initial conditions at start of simulation\n" + \
            "              ran from 1990 to end of 1992 (pat 1-11-95) RUN 21 ***\n" + \
            "    # -  # ***  CEPS      SURS       UZS      IFWS       LZS      AGWS      GWVS\n"
        pwat_state1 = ""
        pwater_data = hspf.pwater.itertuples()
        for pwater in pwater_data:
            pwat_state1 += "{:2s}{:3d}{:5s}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}{:10g}\n".format(' ',
                                                                                               pwater.Number,
                                                                                               ' ',
                                                                                               pwater.CEPS,
                                                                                               pwater.SURS,
                                                                                               pwater.UZS,
                                                                                               pwater.IFWS,
                                                                                               pwater.LZS,
                                                                                               pwater.AGWS,
                                                                                               pwater.GWVS)
        footer = "  END PWAT-STATE1\n"
        text = header + pwat_state1 + footer
        return text

    def write_hspf_implnd_block_text(self, hspf):
        header = "IMPLND\n"
        gen_info = self.write_hspf_implnd_gen_info_text(hspf) + "\n"
        activity = self.write_hspf_implnd_activity_text() + "\n"
        iwat_parm1 = self.write_hspf_implnd_iwat_parm1_text() + "\n"
        iwat_parm2 = self.write_hspf_implnd_iwat_parm2_text(hspf) + "\n"
        iwat_parm3 = self.write_hspf_implnd_iwat_parm3_text(hspf) + "\n"
        iwat_state1 = self.write_hspf_implnd_iwat_state1_text() + "\n"
        footer = "END IMPLND\n"
        text = header + gen_info + activity + iwat_parm1 + iwat_parm2 + iwat_parm3 + iwat_state1 + footer
        return text

    def write_hspf_implnd_gen_info_text(self, hspf):
        header = \
        "  GEN-INFO\n" +\
        "    <PLS ><-------Name------->   Unit-systems   Printer ***\n" +\
        "    # -  #                     User  t-series Engl Metr ***\n" +\
        "                                      in  out           ***\n"
        gen_info = ""
        for implnd in hspf.implnds:
            gen_info += "{:2s}{:3d}{:5s}{:24s}{:1d}{:5d}{:5d}{:10d}\n".format(' ', implnd.implnd_id, ' ', implnd.desc, 1, 0, 0, 0)

        footer = "  END GEN-INFO\n"
        text = header + gen_info + footer
        return text

    def write_hspf_implnd_activity_text(self):
        header = \
        "  ACTIVITY\n"+\
        "    <PLS > ************* Active Sections *****************************\n" +\
        "     # -  # ATMP SNOW IWAT  SLD  IWG IQAL   ***\n"

        activity =\
        "    1  999    0    0    1    0    0    0\n"
        footer = "  END ACTIVITY\n"
        text = header + activity + footer
        return text

    def write_hspf_implnd_iwat_parm1_text(self):
        header = \
            "  IWAT-PARM1\n" + \
            "    <PLS >  IWATER variable monthly parameter value flags  ***\n" + \
            "    # -  # CSNO RTOP  VRS  VNN RTLI     ***\n"
        iwat_parm1 = "    1  999    0    0    0    0    0 \n"
        footer = "  END IWAT-PARM1\n"
        text = header + iwat_parm1 + footer
        return text

    def write_hspf_implnd_iwat_parm2_text(self, hspf):
        header = \
            "  IWAT-PARM2\n" + \
            "    <PLS >      IWATER input info: Part 2         ***\n" + \
            "    # -  # ***  LSUR     SLSUR      NSUR     RETSC\n"

        iwater_data = hspf.iwater.itertuples()
        iwat_parm2 = ""
        for iwater in iwater_data:
            iwat_parm2 += "{:2s}{:3d}{:5s}{:10g}{:10g}{:10g}{:10g}\n".format(' ',
                                                                             iwater.Number,
                                                                             ' ',
                                                                             iwater.LSUR,
                                                                             iwater.SLSUR,
                                                                             iwater.NSUR,
                                                                             iwater.RETSC)

        footer = "  END IWAT-PARM2\n"
        text = header + iwat_parm2 + footer
        return text

    def write_hspf_implnd_iwat_parm3_text(self, hspf):
        header = \
        "  IWAT-PARM3\n"+\
        "    <PLS >      IWATER input info: Part 3         ***\n" +\
        "    # -  # ***PETMAX    PETMIN \n"
        iwater_data = hspf.iwater.itertuples()
        iwat_parm3 = ""
        for iwater in iwater_data:
            iwat_parm3 += "{:2s}{:3d}{:5s}{:10g}{:10g}\n".format(' ',
                                                                 iwater.Number,
                                                                 ' ',
                                                                 iwater.PETMAX,
                                                                 iwater.PETMIN)

        footer = "  END IWAT-PARM3\n"
        text = header + iwat_parm3 + footer
        return text

    def write_hspf_implnd_iwat_state1_text(self):
        header = \
        "  IWAT-STATE1\n"+\
        "    <PLS > *** Initial conditions at start of simulation\n" +\
        "    # -  # ***  RETS      SURS\n"
        state = "    1  999         0         0\n"
        footer = "  END IWAT-STATE1\n"
        text = header + state + footer
        return text

    def write_hspf_ext_sources_as_text(self, rg, rg_multiplier, evap, evap_multiplier, hru):
        evap = 2
        # TODO EVAP DSN should not be hardwired
        header = \
        "EXT SOURCES\n"+\
        "<-Volume-> <Member> SsysSgap<--Mult-->Tran <-Target vols> <-Grp> <-Member->  ***\n"+\
        "<Name>   # <Name> # tem strg<-factor->strg <Name>   #   #        <Name> # #  ***\n"

        sources = \
        "WDM1  " + "{:4d}".format(rg) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1 999 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(rg) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1 999 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"

        precip_to_dss = \
        "WDM1   " + "{:3d}".format(rg) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          COPY    15     INPUT  MEAN   1 1\n\n"

# Is this used or can it be deleted
        obs_flow_to_dss = \
        "WDM3   " + "{:3d}".format(1) + " FLOW     ENGL    " + "{:4.3f}".format(1) + "          COPY    16     INPUT  MEAN   1 1\n\n"

        footer = "END EXT SOURCES\n"

        if hru:
            text = header + sources + footer
        else:
            text = header + sources + precip_to_dss + obs_flow_to_dss + footer
        return text

    def write_hspf_ext_sources_as_text_multiple_rgs (self, rg, rg_multiplier, evap, evap_multiplier, hru):
        # evap = 2
        # TODO EVAP DSN should not be hardwired
        header = \
        "EXT SOURCES\n"+\
        "<-Volume-> <Member> SsysSgap<--Mult-->Tran <-Target vols> <-Grp> <-Member->  ***\n"+\
        "<Name>   # <Name> # tem strg<-factor->strg <Name>   #   #        <Name> # #  ***\n"

        sources = \
        "WDM1  " + "{:4d}".format(192) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1  99 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(192) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1  99 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(10) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 101 199 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(10) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 101 199 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 301 399 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 301 399 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 401 499 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 401 499 EXTNL  PREC\n" +\
        "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"

        # sources = \
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(193) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"

        # sources = \
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(161) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"

        # sources = \
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(227) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"
        #
        # sources = \
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(172) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"

        # sources = \
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND   1  99 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 101 199 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 201 299 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 301 399 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          PERLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(234) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          IMPLND 401 499 EXTNL  PREC\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:4.3f}".format(evap_multiplier) + "          PERLND   1 999 EXTNL  PETINP\n" +\
        # "WDM1  " + "{:4d}".format(evap) + " EVAP     ENGL    " + "{:3.3f}".format(evap_multiplier) + "          IMPLND   1 999 EXTNL  PETINP\n"

        # TODO is this needed
        precip_to_dss = \
        "WDM1   " + "{:3d}".format(rg) + " PREC     ENGL    " + "{:4.3f}".format(rg_multiplier) + "          COPY    15     INPUT  MEAN   1 1\n\n"

        # TODO is this needed
        obs_flow_to_dss = \
        "WDM3   " + "{:3d}".format(1) + " FLOW     ENGL    " + "{:4.3f}".format(1) + "          COPY    16     INPUT  MEAN   1 1\n\n"

        footer = "END EXT SOURCES\n"

        if hru:
            text = header + sources + footer
        else:
            text = header + sources + precip_to_dss + obs_flow_to_dss + footer
        return text

    def write_hspf_ext_targets_as_text(self):
        header = "EXT TARGETS\n" +\
            "<-Volume-> <-Grp> <-Member-><--Mult-->Tran <-Volume-> <Member> Tsys Tgap Amd ***\n" +\
            "<Name>   #        <Name> # #<-factor->strg <Name>   # <Name>    tem strg strg***\n"
        rchres =      "RCHRES   1 HYDR   RO                1      WDM2  1010 FLOW     ENGL      REPL\n" +\
                      "RCHRES   1 HYDR   RO                1 AVER DSS   1010 FLOW     ENGL      REPL\n"
        perlnd_suro = "COPY    11 OUTPUT MEAN   1 1    145.2      WDM2  1011 FLOW     ENGL      REPL\n" +\
                      "COPY    11 OUTPUT MEAN   1 1    145.2 AVER DSS   1011 FLOW     ENGL      REPL\n"
        perlnd_ifwo = "COPY    12 OUTPUT MEAN   2 1    145.2      WDM2  1012 FLOW     ENGL      REPL\n" +\
                      "COPY    12 OUTPUT MEAN   2 1    145.2 AVER DSS   1012 FLOW     ENGL      REPL\n"
        perlnd_agwo = "COPY    13 OUTPUT MEAN   3 1    145.2      WDM2  1013 FLOW     ENGL      REPL\n" +\
                      "COPY    13 OUTPUT MEAN   3 1    145.2 AVER DSS   1013 FLOW     ENGL      REPL\n"
        implnd_suro = "COPY    14 OUTPUT MEAN   1 1    145.2      WDM2  1014 FLOW     ENGL      REPL\n" +\
                      "COPY    14 OUTPUT MEAN   1 1    145.2 AVER DSS   1014 FLOW     ENGL      REPL\n"
        precip =      "COPY    15 OUTPUT MEAN   1 1        1 AVER DSS   1015 PREC     ENGL      REPL\n"
        footer = "END EXT TARGETS"
        text = header + rchres + perlnd_suro + perlnd_ifwo + perlnd_agwo + implnd_suro + precip + footer
        return text

    def write_hspf_dss_path_names_block_as_text(self, rg, name):
        name = name.replace(" ", "_")
        if len(name) > 20:
            name = name[0:20]
        header = "PATHNAMES\n" +\
                 "<ds> # <ctype-> <**********************Pathname*******************************>\n"
        routed = "1010 1 PER-AVER /" + name + "/RCHRES1/FLOW//5MIN/Lumped" + str(rg) + "/\n"
        unrouted_suro_perlnd = "1011 1 PER-AVER /" + name + "/SURO-PERLND-COPY11/FLOW//5MIN/Lumped" + str(rg) + "/\n"
        unrouted_ifwo_perlnd = "1012 1 PER-AVER /" + name + "/IFWO-PERLND-COPY12/FLOW//5MIN/Lumped" + str(rg) + "/\n"
        unrouted_agwo_perlnd = "1013 1 PER-AVER /" + name + "/AGWO-PERLND-COPY13/FLOW//5MIN/Lumped" + str(rg) + "/\n"
        unrouted_suro_implnd = "1014 1 PER-AVER /" + name + "/SURO-IMPLND-COPY14/FLOW//5MIN/Lumped" + str(rg) + "/\n"
        precipitation = "1015 1 PER-AVER /" + name + "/RAIN GAGE" + str(rg) + "/PREC//5MIN/Lumped" + str(rg) + "/\n"
        footer = "END PATHNAMES\n"
        text = header + routed + unrouted_suro_perlnd + unrouted_ifwo_perlnd + unrouted_agwo_perlnd + \
               unrouted_suro_implnd + precipitation + footer
        return text

    def write_hspf_hru_ext_targets_as_text(self, hspf):
        header = "EXT TARGETS\n" +\
            "<-Volume-> <-Grp> <-Member-><--Mult-->Tran <-Volume-> <Member> Tsys Tgap Amd ***\n" +\
            "<Name>   #        <Name> # #<-factor->strg <Name>   # <Name>    tem strg strg***\n" +\
            "*** 145.2 acft/5min to CFS\n"

        perlnd_suro = "***SURO\n"
        perlnd_ifwo = "***IFWO\n"
        perlnd_agwo = "***AGWO\n"
        for perlnd in hspf.perlnds:
            dsn_suro = perlnd.perlnd_id + hspf.perlnd_surface_flow_base_dsn
            dsn_ifwo = perlnd.perlnd_id + hspf.perlnd_inter_flow_base_dsn
            dsn_agwo = perlnd.perlnd_id + hspf.perlnd_base_flow_base_dsn
            perlnd_suro += "COPY   {:3d} OUTPUT MEAN   1 1 {:8g}{:>10s} {:5d} FLOW     ENGL      REPL\n".format(
                                                                                               perlnd.perlnd_id,
                                                                                               145.2,
                                                                                               "WDM2",
                                                                                               dsn_suro)
            perlnd_ifwo += "COPY   {:3d} OUTPUT MEAN   2 1 {:8g}{:>10s} {:5d} FLOW     ENGL      REPL\n".format(
                                                                                               perlnd.perlnd_id,
                                                                                               145.2,
                                                                                               "WDM3",
                                                                                               dsn_ifwo)
            perlnd_agwo += "COPY   {:3d} OUTPUT MEAN   3 1 {:8g}{:>10s} {:5d} FLOW     ENGL      REPL\n".format(
                                                                                               perlnd.perlnd_id,
                                                                                               145.2,
                                                                                               "WDM4",
                                                                                               dsn_agwo)
        implnd_suro = "***SURO\n"
        for implnd in hspf.implnds:
            dsn_suro = implnd.implnd_id + hspf.implnd_surface_flow_base_dsn
            implnd_copy_number = implnd.implnd_id + 500 #TODO should not be hardwired
            implnd_suro += "COPY   {:3d} OUTPUT MEAN   1 1 {:8g}{:>10s} {:5d} FLOW     ENGL      REPL\n".format(
                                                                                               implnd_copy_number,
                                                                                               145.2,
                                                                                               "WDM2",
                                                                                               dsn_suro)
        footer = "END EXT TARGETS"
        text = header + perlnd_suro + perlnd_ifwo + perlnd_agwo + implnd_suro + footer
        return text

    def write_hspf_hru_schematic_block_text(self, hspf):
        header = "SCHEMATIC\n" + \
                 "<-Source->                  <--Area-->     <-Target->   MBLK   ***\n" + \
                 "<Name>   #                  <-factor->     <Name>   #   Tbl#   ***\n"
        footer = "END SCHEMATIC\n"
        perlnd_suro_string = "***SURO\n"
        perlnd_ifwo_string = "***IFWO\n"
        perlnd_agwo_string = "***AGWO\n"
        implnd_string = "***SURO\n"
        for perlnd_id in hspf.perlnd_ids():
            perlnd_suro_string += "PERLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                           ' ',
                                                                                           hspf.hru_area_in_acres,
                                                                                           perlnd_id,
                                                                                           ' ',
                                                                                           self.perlnd_suro_to_copy_masslink)

            perlnd_ifwo_string += "PERLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                           ' ',
                                                                                                   hspf.hru_area_in_acres,
                                                                                                   perlnd_id,
                                                                                           ' ',
                                                                                                   self.perlnd_ifwo_to_copy_masslink)

            perlnd_agwo_string += "PERLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                           ' ',
                                                                                                   hspf.hru_area_in_acres,
                                                                                                   perlnd_id,
                                                                                           ' ',
                                                                                                   self.perlnd_agwo_to_copy_masslink)

        for implnd_id in hspf.implnd_ids():
            implnd_string += "IMPLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(implnd_id,
                                                                                           ' ',
                                                                                              hspf.hru_area_in_acres,
                                                                                              implnd_id + 500, #TODO should not be hardwired
                                                                                           ' ',
                                                                                              self.implnd_suro_to_copy_masslink)

        text = header + perlnd_suro_string + perlnd_ifwo_string + perlnd_agwo_string + implnd_string + footer
        return text



    def write_individual_subbasins_to_dataframe(self, hspf, subbasins):
        subbasin_perlnd_implnd_dicts = []
        for subbasin in hspf.subbasins:
            subbasin_perlnd_implnd_dict = {}
            subbasin_perlnd_implnd_dict['NAME'] = subbasin.subbasin_name
            subbasin_perlnd_implnd_dict['SURO'] = subbasin.outlet_surface_flow
            subbasin_perlnd_implnd_dict['IFWO'] = subbasin.outlet_inter_flow
            subbasin_perlnd_implnd_dict['AGWO'] = subbasin.outlet_base_flow
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[str(perlnd.perlnd_id) + "_" + perlnd.desc + "_suro"] = perlnd.area * subbasin.surfaceflow_area_factor
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[str(perlnd.perlnd_id) + "_" + perlnd.desc + "_ifwo"] = perlnd.area * subbasin.interflow_area_factor
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[str(perlnd.perlnd_id) + "_" + perlnd.desc + "_agwo"] = perlnd.area * subbasin.baseflow_area_factor
            for implnd in subbasin.implnds:
                subbasin_perlnd_implnd_dict[str(implnd.implnd_id) + "_" + implnd.desc] = implnd.area
            if not subbasin.outlet_surface_flow is None \
                or not subbasin.outlet_surface_flow is None \
                    or not subbasin.outlet_base_flow is None:
                subbasin_perlnd_implnd_dicts.append(subbasin_perlnd_implnd_dict)
        for subbasin in hspf.explicit_impervious_area_subbasins:
            subbasin_perlnd_implnd_dict = {}
            subbasin_perlnd_implnd_dict['NAME'] = subbasin.subbasin_name
            subbasin_perlnd_implnd_dict['SURO'] = subbasin.outlet_surface_flow
            subbasin_perlnd_implnd_dict['IFWO'] = subbasin.outlet_inter_flow
            subbasin_perlnd_implnd_dict['AGWO'] = subbasin.outlet_base_flow
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[
                    str(perlnd.perlnd_id) + "_" + perlnd.desc + "_suro"] = perlnd.area * subbasin.surfaceflow_area_factor
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[
                    str(perlnd.perlnd_id) + "_" + perlnd.desc + "_ifwo"] = perlnd.area * subbasin.interflow_area_factor
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[
                    str(perlnd.perlnd_id) + "_" + perlnd.desc + "_agwo"] = perlnd.area * subbasin.baseflow_area_factor
            for implnd in subbasin.implnds:
                subbasin_perlnd_implnd_dict[str(implnd.implnd_id) + "_" + implnd.desc] = implnd.area
            if not subbasin.outlet_surface_flow is None \
                    or not subbasin.outlet_surface_flow is None \
                    or not subbasin.outlet_base_flow is None:
                subbasin_perlnd_implnd_dicts.append(subbasin_perlnd_implnd_dict)

        for subbasin in hspf.future_area_subbasins:
            subbasin_perlnd_implnd_dict = {}
            subbasin_perlnd_implnd_dict['NAME'] = subbasin.subbasin_name
            subbasin_perlnd_implnd_dict['SURO'] = subbasin.outlet_surface_flow
            subbasin_perlnd_implnd_dict['IFWO'] = subbasin.outlet_inter_flow
            subbasin_perlnd_implnd_dict['AGWO'] = subbasin.outlet_base_flow
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[str(perlnd.perlnd_id) + "_" + perlnd.desc + "_suro"] = perlnd.area * subbasin.surfaceflow_area_factor
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[str(perlnd.perlnd_id) + "_" + perlnd.desc + "_ifwo"] = perlnd.area * subbasin.interflow_area_factor
            for perlnd in subbasin.perlnds:
                subbasin_perlnd_implnd_dict[str(perlnd.perlnd_id) + "_" + perlnd.desc + "_agwo"] = perlnd.area * subbasin.baseflow_area_factor
            for implnd in subbasin.implnds:
                subbasin_perlnd_implnd_dict[str(implnd.implnd_id) + "_" + implnd.desc] = implnd.area
            if not subbasin.outlet_surface_flow is None \
                or not subbasin.outlet_surface_flow is None \
                    or not subbasin.outlet_base_flow is None:
                subbasin_perlnd_implnd_dicts.append(subbasin_perlnd_implnd_dict)
        subbasin_dataframe = pd.DataFrame(subbasin_perlnd_implnd_dicts) #.transpose()
        return subbasin_dataframe

    def write_individual_soils_subbasins_to_dataframe(self, hspf, subbasins):
        subbasin_soil_dicts = []
        for subbasin in hspf.subbasins:
            subbasin_soils_dict = {}
            subbasin_soils_dict['NAME'] = subbasin.subbasin_name
            subbasin_soils_dict['SURO'] = subbasin.outlet_surface_flow
            subbasin_soils_dict['IFWO'] = subbasin.outlet_inter_flow
            subbasin_soils_dict['AGWO'] = subbasin.outlet_base_flow
            for key in subbasin.soil_areas.keys():
                subbasin_soils_dict[str(key) + "_" + hspf.soil[key][1]] = subbasin.soil_areas[key]
            subbasin_soil_dicts.append(subbasin_soils_dict)
            subbasin_dataframe = pd.DataFrame(subbasin_soil_dicts)
        return subbasin_dataframe

    def write_hspf_schematic_block_individual_subbasins_text(self, hspf, subbasins):
        header = "SCHEMATIC\n" + \
                 "<-Source->                  <--Area-->     <-Target->   MBLK ***\n" + \
                 "<Name>   #                  <-factor->     <Name>   #   Tbl# ***\n"
        footer = "END SCHEMATIC\n"
        perlnd_suro_string = "***PERLND SURO\n"
        perlnd_suro_copy = "***SURO PERLND Unrouted\n"
        perlnd_ifwo_string = "***IFWO\n"
        perlnd_ifwo_copy = "***IFWO PERLND Unrouted\n"
        perlnd_agwo_string = "***AGWO\n"
        perlnd_agwo_copy = "***AGWO PERLND Unrouted\n"
        implnd_string = "***IMPLND SURO\n"
        implnd_suro_copy = "***SURO IMPLND Unrouted\n"

        text = header
        for subbasin in subbasins:
            text += "***Subbasin " + subbasin.subbasin_name +"\n"
            perlnd_suro_string = ""
            for perlnd_id in hspf.perlnd_ids():
                total_perlnd_area = 0
                if subbasin.outlet_surface_flow is not None:
                    for perlnd in subbasin.perlnds:
                        if perlnd.perlnd_id == perlnd_id:
                            total_perlnd_area += perlnd.area
                if total_perlnd_area > 0:
                    perlnd_suro_string += "PERLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                                   ' ',
                                                                                                   total_perlnd_area,
                                                                                                   1,
                                                                                                   ' ',
                                                                                                   self.perlnd_suro_to_rchres_masslink)
            text += perlnd_suro_string + "\n"

            perlnd_ifwo_string = ""
            for perlnd_id in hspf.perlnd_ids():
                total_perlnd_area = 0
                if subbasin.outlet_inter_flow is not None:
                    for perlnd in subbasin.perlnds:
                        if perlnd.perlnd_id == perlnd_id:
                            total_perlnd_area += perlnd.area
                if total_perlnd_area > 0:
                    perlnd_ifwo_string += "PERLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                                   ' ',
                                                                                                   total_perlnd_area,
                                                                                                   1,
                                                                                                   ' ',
                                                                                                   self.perlnd_ifwo_to_rchres_masslink)
            text += perlnd_ifwo_string + "\n"

            perlnd_agwo_string = ""
            for perlnd_id in hspf.perlnd_ids():
                total_perlnd_area = 0
                if subbasin.outlet_base_flow is not None:
                    for perlnd in subbasin.perlnds:
                        if perlnd.perlnd_id == perlnd_id:
                            total_perlnd_area += perlnd.area
                if total_perlnd_area > 0:
                    perlnd_agwo_string += "PERLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                                   ' ',
                                                                                                   total_perlnd_area,
                                                                                                   1,
                                                                                                   ' ',

                                                                                               self.perlnd_agwo_to_rchres_masslink)
            text += perlnd_agwo_string + "\n"

            implnd_string = ""
            for implnd_id in hspf.implnd_ids():
                total_implnd_area = 0
                if subbasin.outlet_surface_flow is not None:
                    for implnd in subbasin.implnds:
                        if implnd.implnd_id == implnd_id:
                            total_implnd_area += implnd.area
                if total_implnd_area > 0:
                    implnd_string += "IMPLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(implnd_id,
                                                                                                   ' ',
                                                                                                   total_implnd_area,
                                                                                                   1,
                                                                                                   ' ',
                                                                                                   self.implnd_suro_to_rchres_masslink)
            text += implnd_string + "\n"

        text += footer
        return text

    def write_hspf_schematic_block_text(self, hspf, subbasins):
        header = "SCHEMATIC\n" + \
                 "<-Source->                  <--Area-->     <-Target->   MBLK ***\n" + \
                 "<Name>   #                  <-factor->     <Name>   #   Tbl# ***\n"
        footer = "END SCHEMATIC\n"
        perlnd_suro_string = "***PERLND SURO\n"
        perlnd_suro_copy = "***SURO PERLND Unrouted\n"
        perlnd_ifwo_string = "***IFWO\n"
        perlnd_ifwo_copy = "***IFWO PERLND Unrouted\n"
        perlnd_agwo_string = "***AGWO\n"
        perlnd_agwo_copy = "***AGWO PERLND Unrouted\n"
        implnd_string = "***IMPLND SURO\n"
        implnd_suro_copy = "***SURO IMPLND Unrouted\n"
        for perlnd_id in hspf.perlnd_ids():
            total_perlnd_area = 0
            for subbasin in subbasins:
                if subbasin.outlet_surface_flow is not None:
                    for perlnd in subbasin.perlnds:
                        if perlnd.perlnd_id == perlnd_id:
                            total_perlnd_area += perlnd.area
            if total_perlnd_area > 0:
                perlnd_suro_string += "PERLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                               ' ',
                                                                                               total_perlnd_area * subbasin.surfaceflow_area_factor,
                                                                                               1,
                                                                                               ' ',
                                                                                               self.perlnd_suro_to_rchres_masslink)
                perlnd_suro_copy += "PERLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                               ' ',
                                                                                               total_perlnd_area * subbasin.surfaceflow_area_factor,
                                                                                               11,
                                                                                               ' ',
                                                                                               self.perlnd_suro_to_copy_masslink)
        for perlnd_id in hspf.perlnd_ids():
            total_perlnd_area = 0
            for subbasin in subbasins:
                if subbasin.outlet_inter_flow is not None:
                    for perlnd in subbasin.perlnds:
                        if perlnd.perlnd_id == perlnd_id:
                            total_perlnd_area += perlnd.area
            if total_perlnd_area > 0:
                perlnd_ifwo_string += "PERLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                               ' ',
                                                                                               total_perlnd_area * subbasin.interflow_area_factor,
                                                                                               1,
                                                                                               ' ',
                                                                                               self.perlnd_ifwo_to_rchres_masslink)
                perlnd_ifwo_copy += "PERLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                                       ' ',
                                                                                                       total_perlnd_area * subbasin.interflow_area_factor,
                                                                                                       12,
                                                                                                       ' ',
                                                                                                       self.perlnd_ifwo_to_copy_masslink)
        for perlnd_id in hspf.perlnd_ids():
            total_perlnd_area = 0
            for subbasin in subbasins:
                if subbasin.outlet_base_flow is not None:
                    for perlnd in subbasin.perlnds:
                        if perlnd.perlnd_id == perlnd_id:
                            total_perlnd_area += perlnd.area
            if total_perlnd_area > 0:
                perlnd_agwo_string += "PERLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                               ' ',
                                                                                               total_perlnd_area * subbasin.baseflow_area_factor,
                                                                                               1,
                                                                                               ' ',

                                                                                           self.perlnd_agwo_to_rchres_masslink)
                perlnd_agwo_copy += "PERLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(perlnd_id,
                                                                                                       ' ',
                                                                                                       total_perlnd_area  * subbasin.baseflow_area_factor,
                                                                                                       13,
                                                                                                       ' ',
                                                                                                       self.perlnd_agwo_to_copy_masslink)

        for implnd_id in hspf.implnd_ids():
            total_implnd_area = 0
            for subbasin in subbasins:
                if subbasin.outlet_surface_flow is not None:
                    for implnd in subbasin.implnds:
                        if implnd.implnd_id == implnd_id:
                            total_implnd_area += implnd.area
            if total_implnd_area > 0:
                implnd_string += "IMPLND {:3d}{:18s}{:10f}     RCHRES {:3d}{:4s}{:3d}\n".format(implnd_id,
                                                                                               ' ',
                                                                                               total_implnd_area * subbasin.surfaceflow_area_factor,
                                                                                               1,
                                                                                               ' ',
                                                                                               self.implnd_suro_to_rchres_masslink)
                implnd_suro_copy += "IMPLND {:3d}{:18s}{:10.3f}     COPY   {:3d}{:4s}{:3d}\n".format(implnd_id,
                                                                                                   ' ',
                                                                                                   total_implnd_area * subbasin.surfaceflow_area_factor,
                                                                                                   14,
                                                                                                   ' ',
                                                                                                   self.implnd_suro_to_copy_masslink)

        text = header + perlnd_suro_string + perlnd_ifwo_string + perlnd_agwo_string + implnd_string + \
               perlnd_suro_copy + perlnd_ifwo_copy + perlnd_agwo_copy + implnd_suro_copy + \
               footer
        return text

    def write_hspf_mass_link_as_text(self):
        header = \
        "MASS-LINK\n" +\
        "<Volume>   <-Grp> <-Member-><--Mult-->     <Target>       <-Grp> <-Member->***\n" +\
        "<Name>            <Name> # #<-factor->     <Name>                <Name> # #***\n"

        mass_links = \
        "  MASS-LINK        2\n" + \
        "PERLND     PWATER SURO       0.083333      RCHRES         INFLOW IVOL\n" + \
        "  END MASS-LINK    2\n\n" +\
        "  MASS-LINK        3\n" + \
        "PERLND     PWATER IFWO       0.083333      RCHRES         INFLOW IVOL\n" + \
        "  END MASS-LINK    3\n\n" +\
        "  MASS-LINK        4\n" + \
        "PERLND     PWATER AGWO       0.083333      RCHRES         INFLOW IVOL\n" + \
        "  END MASS-LINK    4\n\n" +\
        "  MASS-LINK        5\n" + \
        "IMPLND     IWATER SURO       0.083333      RCHRES         INFLOW IVOL\n" + \
        "  END MASS-LINK    5\n\n" +\
        "  MASS-LINK       12\n" + \
        "PERLND     PWATER SURO       0.083333      COPY           INPUT  MEAN   1  \n" + \
        "  END MASS-LINK   12\n\n" +\
        "  MASS-LINK       13\n" + \
        "PERLND     PWATER IFWO       0.083333      COPY           INPUT  MEAN   2  \n" + \
        "  END MASS-LINK   13\n\n" +\
        "  MASS-LINK       14\n" + \
        "PERLND     PWATER AGWO       0.083333      COPY           INPUT  MEAN   3  \n" + \
        "  END MASS-LINK   14\n\n" +\
        "  MASS-LINK       15\n" + \
        "IMPLND     IWATER SURO       0.083333      COPY           INPUT  MEAN   1  \n" + \
        "  END MASS-LINK   15\n"
        footer = "END MASS-LINK\n"
        text = header + mass_links + footer
        return text

    def create_blank_routed_flow_wdm(self, hspf, output_blank_wdm_file_path):
        # print("Create wdm")
        wdmtoolbox.createnewwdm(output_blank_wdm_file_path, True)
        tcode = 2
        tstep = hspf.input_timestep_in_minutes

        tstype = 'FLOW'
        base_year = 1948
        scenario = "simulate"
        constituent = 'FLOW'
        tsfill = 0.0  # TODO need to provide feedback on fill

        dsn = 1010
        statid = str(dsn)
        location = "RoutFlow"
        description = "Routed Flow at Outlet"
        wdmtoolbox.createnewdsn(output_blank_wdm_file_path, dsn, tstype, base_year, tcode, tstep, statid, scenario,
                                location, description, constituent, tsfill)
        dsn = 1011
        statid = str(dsn)
        location = "PERLSURO"
        description = "Unrouted Pervious SURO for model"
        wdmtoolbox.createnewdsn(output_blank_wdm_file_path, dsn, tstype, base_year, tcode, tstep, statid, scenario,
                                location, description, constituent, tsfill)
        dsn = 1012
        statid = str(dsn)
        location = "IFWO"
        description = "Unrouted IFWO for model"
        wdmtoolbox.createnewdsn(output_blank_wdm_file_path, dsn, tstype, base_year, tcode, tstep, statid, scenario,
                                location, description, constituent, tsfill)
        dsn = 1013
        statid = str(dsn)
        location = "AGWO"
        description = "Unrouted AGWO for model"
        wdmtoolbox.createnewdsn(output_blank_wdm_file_path, dsn, tstype, base_year, tcode, tstep, statid, scenario,
                                location, description, constituent, tsfill)

        dsn = 1014
        statid = str(dsn)
        location = "IMPLSURO"
        description = "Unrouted Impervious SURO for model"
        wdmtoolbox.createnewdsn(output_blank_wdm_file_path, dsn, tstype, base_year, tcode, tstep, statid, scenario,
                                location, description, constituent, tsfill)

    def read_lumped_model_flow_data(self, wdm_file_path, dsn):
        flow_data = wdmtoolbox.extract(wdm_file_path, dsn)
        return flow_data

    def create_blank_unrouted_flow_wdm(self, hspf: Hspf, output_blank_wdm_file_path_suro, output_blank_wdm_file_path_ifwo, output_blank_wdm_file_path_agwo):
        # print("Create wdm")
        wdmtoolbox.createnewwdm(output_blank_wdm_file_path_suro, True)

        wdmtoolbox.createnewwdm(output_blank_wdm_file_path_ifwo, True)

        wdmtoolbox.createnewwdm(output_blank_wdm_file_path_agwo, True)

        tcode = 2
        tstep = hspf.input_timestep_in_minutes

        perlnds = hspf.perlnds
        implnds = hspf.implnds

        self.create_blank_unrouted_flow_perlnd_dsns(output_blank_wdm_file_path_suro, tcode, tstep, "SURO",
                                                    hspf.perlnd_surface_flow_base_dsn, perlnds)

        self.create_blank_unrouted_flow_perlnd_dsns(output_blank_wdm_file_path_ifwo, tcode, tstep, "IFWO",
                                                    hspf.perlnd_inter_flow_base_dsn, perlnds)

        self.create_blank_unrouted_flow_perlnd_dsns(output_blank_wdm_file_path_agwo, tcode, tstep, "AGWO",
                                                    hspf.perlnd_base_flow_base_dsn, perlnds)

        self.create_blank_unrouted_flow_implnd_dsns(output_blank_wdm_file_path_suro, tcode, tstep, "SURO",
                                                    hspf.implnd_surface_flow_base_dsn, implnds)

    def copy_obs_data_dss(self, obs_flow_dss, simulation_dsn):
        shutil.copyfile(obs_flow_dss, simulation_dsn)

    def create_blank_unrouted_flow_perlnd_dsns(self, output_blank_wdm_file_path, tcode: int, tstep: int, flow_type: str,
                                      flow_type_base_dsn: int, perlnds: List[Perlnd]):
        for perlnd in perlnds:
            dsn = flow_type_base_dsn + perlnd.perlnd_id
            description = flow_type + " " + perlnd.desc
            location = str(dsn)
            self.create_blank_unrouted_flow_dsn(output_blank_wdm_file_path, dsn, tcode, tstep, description, location)

    def create_blank_unrouted_flow_implnd_dsns(self, output_blank_wdm_file_path, tcode: int, tstep: int, flow_type: str,
                                      flow_type_base_dsn: int, implnds: List[Implnd]):
        for implnd in implnds:
            dsn = flow_type_base_dsn + implnd.implnd_id
            description = flow_type + " " + implnd.desc
            location = str(dsn)
            self.create_blank_unrouted_flow_dsn(output_blank_wdm_file_path, dsn, tcode, tstep, description, location)

    def create_blank_unrouted_flow_dsn(self, output_blank_wdm_file_path: str, dsn: int, tcode: int, tstep: int, description: str,
                              location: str):
        tstype = 'FLOW'
        base_year = 1948
        statid = str(dsn)
        scenario = "simulate"
        location = location
        description = description
        constituent = 'FLOW'
        tsfill = 0.0  # TODO need to provide feedback on fill
        wdmtoolbox.createnewdsn(output_blank_wdm_file_path, dsn, tstype, base_year, tcode, tstep, statid, scenario,
                                location, description, constituent, tsfill)

    def run_hspf(self, working_directory, uci_file_name, winhspflt_executable_path):
        arguments = winhspflt_executable_path + " " + uci_file_name
        subprocess.check_call(arguments, cwd=working_directory, shell=True)

    def run_swmm(self, working_directory, name_of_swmm_inp_file, name_of_swmm_rpt_file,
                      name_of_swmm_out_file, swmm_executable_path):
        arguments = "\"" + swmm_executable_path + "\"" + " " + \
                    name_of_swmm_inp_file + " " + \
                    name_of_swmm_rpt_file + " " + \
                    name_of_swmm_out_file
        subprocess.check_call(arguments, cwd=working_directory, shell=True)

    def copy_swmm_inp(self, input_swmm_inp_file_path, simulation_swmm_inp_file_path, start_date, stop_date,
                      reporting_time_step='00:05:00', routing_time_step_in_seconds=5, links_to_report=None, all_links=False, all_nodes=False,
                      dynamic_wave = True):

        routing_hours = int((routing_time_step_in_seconds - (routing_time_step_in_seconds % 3600))/3600)
        routing_minutes = int(((routing_time_step_in_seconds - routing_hours*3600) - (routing_time_step_in_seconds - routing_hours*3600) % 60)/60)
        routing_seconds = int(routing_time_step_in_seconds - routing_hours * 3600 - routing_minutes * 60)

        routing_time_step_string = "{:02d}:{:02d}:{:02d} ".format(routing_hours, routing_minutes, routing_seconds)

        with open(input_swmm_inp_file_path, 'r') as input_swmm_inp:
            inp = ""
            line = " "
            while line is not '':
                if dynamic_wave == True:
                    routing = "DYNWAVE"
                else:
                    routing = "KINWAVE"
                line = input_swmm_inp.readline()
                if line[0:9] == "[OPTIONS]":
                    inp += "[OPTIONS]\n" + \
                           ";;Option Value\n" + \
                           "FLOW_UNITS CFS\n" + \
                           "INFILTRATION GREEN_AMPT\n" + \
                           "FLOW_ROUTING " + routing + "\n" + \
                           "LINK_OFFSETS ELEVATION\n" + \
                           "MIN_SLOPE 0\n" + \
                           "ALLOW_PONDING YES\n" + \
                           "SKIP_STEADY_STATE NO\n" + \
                           "\n" + \
                           "IGNORE_RAINFALL YES\n" + \
                           "START_DATE " + start_date + "\n" + \
                           "START_TIME 00:00:00\n" +\
                    "REPORT_START_DATE " + start_date + "\n" +\
                    "REPORT_START_TIME 00:00:00\n" +\
                    "END_DATE " + stop_date + "\n" +\
                    "END_TIME 00:00:00\n" +\
                    "SWEEP_START 01/01\n" +\
                    "SWEEP_END 12/31\n" +\
                    "DRY_DAYS 0\n" +\
                    "REPORT_STEP " + reporting_time_step + "\n" +\
                    "WET_STEP 00:00:30\n" +\
                    "DRY_STEP 00:00:30\n" +\
                    "ROUTING_STEP " + routing_time_step_string + "\n" +\
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
                           "THREADS 10\n" + \
                           "\n"
                    while line is not '':
                        line = input_swmm_inp.readline()
                        if line[0] == "[":
                            break
                if line[0:8] == "[REPORT]":
                    if links_to_report is not None or all_nodes or all_links:
                        if links_to_report is not None and not all_links:
                            link_report_string = ""
                            for link_number, link in enumerate(links_to_report):
                                if link_number == 0:
                                    link_report_string += "LINKS " + str(link)
                                elif (link_number + 1) % 4 == 0 and link_number > 0:
                                    link_report_string += "\n"
                                    link_report_string += "LINKS " + str(link)
                                else:
                                    link_report_string += " " + str(link)
                            link_report_string += "\n"

                        inp += "[REPORT]\n" + \
                               "INPUT         YES\n" + \
                               "CONTROLS      NO\n" + \
                               "SUBCATCHMENTS NONE\n"
                        if all_nodes:
                            inp += "NODES         ALL\n"
                        else:
                            inp += "NODES         NONE\n"
                        if links_to_report is not None and not all_links:
                            inp += link_report_string + "\n"
                        elif all_links:
                            inp += "LINKS         ALL\n"
                        else:
                            inp += "LINKS         NONE\n"

                    while line is not '':
                            line = input_swmm_inp.readline()
                            if line[0] == "[":
                                break
                if line[0:7] == "[FILES]":
                    inp += "[FILES]\n" +\
                        ";;Interfacing Files \n" +\
                        "USE INFLOWS hspf_to_swmm.txt\n" +\
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
                inp += line
            with open(simulation_swmm_inp_file_path, 'w') as output_swmm_inp:
                output_swmm_inp.write(inp)

    def write_swmm_ini_file(self, simulation_swmm_inp_file_path):
        with open(simulation_swmm_inp_file_path+"\\swmm.ini", 'w') as swmm_ini:
            ini_file = "[SWMM5]\n"
            ini_file += "Version=51010\n"
            ini_file += "[Map]\n"
            ini_file += "ShowGageIDs=0\n"
            ini_file += "ShowSubcatchIDs=0\n"
            ini_file += "ShowSubcatchValues=0\n"
            ini_file += "ShowSubcatchLinks=1\n"
            ini_file += "ShowNodeIDs=0\n"
            ini_file += "ShowNodeValues=0\n"
            ini_file += "ShowNodesBySize=0\n"
            ini_file += "ShowNodeBorder=1\n"
            ini_file += "ShowLinkIDs=0\n"
            ini_file += "ShowLinkValues=0\n"
            ini_file += "ShowLinksBySize=0\n"
            ini_file += "ShowLinkBorder=0\n"
            ini_file += "ShowGages=1\n"
            ini_file += "ShowSubcatchs=1\n"
            ini_file += "ShowNodes=1\n"
            ini_file += "ShowLinks=1\n"
            ini_file += "ShowNodeSymbols=1\n"
            ini_file += "ShowLinkSymbols=1\n"
            ini_file += "ShowLabels=1\n"
            ini_file += "LabelsTranspar=1\n"
            ini_file += "NotationTranspar=0\n"
            ini_file += "SubcatchFillStyle=5\n"
            ini_file += "SubcatchLineSize=1\n"
            ini_file += "SubcatchSnapTol=0\n"
            ini_file += "SubcatchSize=5\n"
            ini_file += "NodeSize=3\n"
            ini_file += "LinkSize=1\n"
            ini_file += "NotationSize=7\n"
            ini_file += "ArrowStyle=0\n"
            ini_file += "ArrowSize=2\n"
            ini_file += "ColorIndex=1\n"
            ini_file += "NotationZoom=100\n"
            ini_file += "LabelZoom=100\n"
            ini_file += "SymbolZoom=100\n"
            ini_file += "ArrowZoom=100\n"
            ini_file += "[Backdrop]\n"
            ini_file += "Visible=0\n"
            ini_file += "Watermark=0\n"
            ini_file += "[Legends]\n"
            ini_file += "NumIntervals=4\n"
            ini_file += "MapSubcatchColor0=16711680\n"
            ini_file += "MapSubcatchColor1=16776960\n"
            ini_file += "MapSubcatchColor2=65280\n"
            ini_file += "MapSubcatchColor3=65535\n"
            ini_file += "MapSubcatchColor4=255\n"
            ini_file += "MapNodeColor0=16711680\n"
            ini_file += "MapNodeColor1=16776960\n"
            ini_file += "MapNodeColor2=65280\n"
            ini_file += "MapNodeColor3=65535\n"
            ini_file += "MapNodeColor4=255\n"
            ini_file += "MapLinkColor0=16711680\n"
            ini_file += "MapLinkColor1=16776960\n"
            ini_file += "MapLinkColor2=65280\n"
            ini_file += "MapLinkColor3=65535\n"
            ini_file += "MapLinkColor4=255\n"
            ini_file += "SubcatchLegend1=25,50,75,100,\n"
            ini_file += "SubcatchLegend2=25,50,75,100,\n"
            ini_file += "SubcatchLegend3=0.5,1,5,10,\n"
            ini_file += "SubcatchLegend4=20,40,60,80,\n"
            ini_file += "SubcatchLegend5=9.99999974737875E-6,25,50,75,\n"
            ini_file += "SubcatchLegend6=0.00999999977648258,0.0500000007450581,0.100000001490116,0.5,\n"
            ini_file += "SubcatchLegend7=0.5,1,3,6,\n"
            ini_file += "SubcatchLegend8=0.00999999977648258,0.0500000007450581,0.100000001490116,0.5,\n"
            ini_file += "SubcatchLegend9=0.00999999977648258,0.0500000007450581,0.100000001490116,0.5,\n"
            ini_file += "SubcatchLegend10=0.00999999977648258,0.0500000007450581,0.100000001490116,0.5,\n"
            ini_file += "SubcatchLegend11=0.00999999977648258,0.0500000007450581,0.100000001490116,0.5,\n"
            ini_file += "SubcatchLegend12=25,50,75,100,\n"
            ini_file += "SubcatchLegend13=0.100000001490116,0.200000002980232,0.300000011920929,0.400000005960464,\n"
            ini_file += "SubcatchLegend14=0.25,0.5,0.75,1,\n"
            ini_file += "NodeLegend1=25,50,75,100,\n"
            ini_file += "NodeLegend2=1,5,10,20,\n"
            ini_file += "NodeLegend3=25,50,75,100,\n"
            ini_file += "NodeLegend4=100,1000,10000,100000,\n"
            ini_file += "NodeLegend5=25,50,75,100,\n"
            ini_file += "NodeLegend6=25,50,75,100,\n"
            ini_file += "NodeLegend7=25,50,75,100,\n"
            ini_file += "NodeLegend8=0.25,0.5,0.75,1,\n"
            ini_file += "LinkLegend1=0.5,1,2,4,\n"
            ini_file += "LinkLegend2=0.00100000004749745,0.00499999988824129,0.00999999977648258,0.100000001490116,\n"
            ini_file += "LinkLegend3=0,1,5,10,\n"
            ini_file += "LinkLegend4=25,50,75,100,\n"
            ini_file += "LinkLegend5=0.5,1,2,4,\n"
            ini_file += "LinkLegend6=0.00999999977648258,0.100000001490116,1,2,\n"
            ini_file += "LinkLegend7=100,1000,10000,100000,\n"
            ini_file += "LinkLegend8=0.25,0.5,0.75,1,\n"
            ini_file += "LinkLegend9=0.25,0.5,0.75,1,\n"
            ini_file += "[Labels]\n"
            ini_file += "Increment=1\n"
            ini_file += "Rain Gage=\n"
            ini_file += "Subcatchment=\n"
            ini_file += "Junction=\n"
            ini_file += "Outfall=\n"
            ini_file += "Divider=\n"
            ini_file += "Storage Unit=\n"
            ini_file += "Conduit=\n"
            ini_file += "Pump=\n"
            ini_file += "Orifice=\n"
            ini_file += "Weir=\n"
            ini_file += "Outlet=\n"
            ini_file += "Label=\n"
            ini_file += "Title / Notes_NextID=1\n"
            ini_file += "Option_NextID=1\n"
            ini_file += "Rain Gage_NextID=1\n"
            ini_file += "Subcatchment_NextID=1\n"
            ini_file += "Junction_NextID=1\n"
            ini_file += "Outfall_NextID=1\n"
            ini_file += "Divider_NextID=1\n"
            ini_file += "Storage Unit_NextID=1\n"
            ini_file += "Conduit_NextID=1\n"
            ini_file += "Pump_NextID=1\n"
            ini_file += "Orifice_NextID=1\n"
            ini_file += "Weir_NextID=1\n"
            ini_file += "Outlet_NextID=1\n"
            ini_file += "Label_NextID=1\n"
            ini_file += "Control Curve_NextID=1\n"
            ini_file += "Diversion Curve_NextID=1\n"
            ini_file += "Pump Curve_NextID=1\n"
            ini_file += "Rating Curve_NextID=1\n"
            ini_file += "Shape Curve_NextID=1\n"
            ini_file += "Storage Curve_NextID=1\n"
            ini_file += "Tidal Curve_NextID=1\n"
            ini_file += "Time Series_NextID=1\n"
            ini_file += "Time Pattern_NextID=1\n"
            ini_file += "Transect_NextID=1\n"
            ini_file += "Unit Hydrograph_NextID=1\n"
            ini_file += "Pollutant_NextID=1\n"
            ini_file += "Land Use_NextID=1\n"
            ini_file += "Aquifer_NextID=1     \n"
            ini_file += "Control Rule_NextID=1\n"
            ini_file += "Climatology_NextID=1\n"
            ini_file += "Snow Pack_NextID=1\n"
            ini_file += "LID Control_NextID=1\n"
            ini_file += "[Defaults]\n"
            ini_file += "SUBCATCH_AREA=5\n"
            ini_file += "SUBCATCH_WIDTH=500\n"
            ini_file += "SUBCATCH_SLOPE=0.5\n"
            ini_file += "SUBCATCH_IMPERV=25\n"
            ini_file += "SUBCATCH_IMPERV_N=0.01\n"
            ini_file += "SUBCATCH_PERV_N=0.1\n"
            ini_file += "SUBCATCH_IMPERV_DS=0.05\n"
            ini_file += "SUBCATCH_PERV_DS=0.05\n"
            ini_file += "SUBCATCH_PCTZERO=25\n"
            ini_file += "NODE_INVERT=0\n"
            ini_file += "NODE_DEPTH=0\n"
            ini_file += "PONDED_AREA=0\n"
            ini_file += "CONDUIT_LENGTH=400\n"
            ini_file += "CONDUIT_SHAPE=CIRCULAR\n"
            ini_file += "CONDUIT_GEOM1=1\n"
            ini_file += "CONDUIT_GEOM2=0\n"
            ini_file += "CONDUIT_GEOM3=0\n"
            ini_file += "CONDUIT_GEOM4=0\n"
            ini_file += "CONDUIT_ROUGHNESS=0.01\n"
            ini_file += "FLOW_UNITS=CFS\n"
            ini_file += "INFILTRATION=GREEN_AMPT\n"
            ini_file += "ROUTING_MODEL=DYNWAVE\n"
            ini_file += "FORCE_MAIN_EQUATION=H-W\n"
            ini_file += "LINK_OFFSETS=ELEVATION\n"
            ini_file += "INFIL_PARAM1=3.0\n"
            ini_file += "INFIL_PARAM2=0.5\n"
            ini_file += "INFIL_PARAM3=4\n"
            ini_file += "INFIL_PARAM4=7\n"
            ini_file += "INFIL_PARAM5=0\n"
            ini_file += "INFIL_PARAM6=\n"
            ini_file += "[Page]\n"
            ini_file += "LeftMargin=1\n"
            ini_file += "RightMargin=1\n"
            ini_file += "TopMargin=1.5\n"
            ini_file += "BottomMargin=1\n"
            ini_file += "HeaderText=D05yr6h\n"
            ini_file += "HeaderAlignment=2\n"
            ini_file += "HeaderEnabled=1\n"
            ini_file += "FooterText=SWMM 5.1\n"
            ini_file += "FooterAlignment=0\n"
            ini_file += "FooterEnabled=1\n"
            ini_file += "PageNumbers=6\n"
            ini_file += "TitleAsHeader=1\n"
            ini_file += "Orientation=0\n"
            ini_file += "[Calibration]\n"
            ini_file += "File1=\n"
            ini_file += "File2=\n"
            ini_file += "File3=\n"
            ini_file += "File4=\n"
            ini_file += "File5=\n"
            ini_file += "File6=\n"
            ini_file += "File7=\n"
            ini_file += "File8=\n"
            ini_file += "File9=\n"
            ini_file += "File10=\n"
            ini_file += "File11=\n"
            ini_file += "File12=\n"
            ini_file += "[Graph]\n"
            ini_file += "DateTimeFormat=\n"
            ini_file += "[Results]\n"
            ini_file += "Saved=1\n"
            ini_file += "Current=1\n"
            swmm_ini.write(ini_file)

    def copy_met_data_wdm(self, input_wdm_filepath, simulation_input_wdm_file_path):
        shutil.copyfile(input_wdm_filepath, simulation_input_wdm_file_path)

    # def copy_unrouted_flow_uci(self, uci_filepath, simulation_uci_filepath, rg):
    #     with open(uci_filepath, 'r') as input_uci:
    #         uci = input_uci.read()
    #         uci = uci.replace('HRU_RG#.wdm', 'HRU{:d}.wdm'.format(rg))
    #         uci = uci.replace('RG#', '{:3d}'.format(rg))
    #         with open(simulation_uci_filepath, 'w') as output_uci:
    #             output_uci.write(uci)

    # def copy_unrouted_design_flow_uci(self, uci_filepath, simulation_uci_filepath, storm_dsn, hru_wdm):
    #     with open(uci_filepath, 'r') as input_uci:
    #         uci = input_uci.read()
    #         uci = uci.replace('#STORM.WDM', hru_wdm)
    #         uci = uci.replace('RG##', '{:4d}'.format(storm_dsn))
    #         with open(simulation_uci_filepath, 'w') as output_uci:
    #             output_uci.write(uci)

    def create_simulation_folder(self, simulation_folder):
        if os.path.exists(simulation_folder):
            print ("simulation folder already exists\n")
        else:
            os.mkdir(simulation_folder)

    def read_hspf_input_file_pwater(self):
        pwater = pd.read_excel(self.input_file, sheet_name='Pervious Parameters (PWater)', header=1)
        return pwater

    def read_hspf_input_file_iwater(self):
        iwater = pd.read_excel(self.input_file, sheet_name='Impervious Parameters (IWater)', header=1)
        return iwater

    def read_hspf_input_file_perlnds(self):
        perlnds = pd.read_excel(self.input_file, sheet_name='Perlnds', header=0)
        return perlnds

    def read_hspf_input_file_implnds(self):
        implnds = pd.read_excel(self.input_file, sheet_name='Implnds', header=0)
        return implnds

    def read_hspf_input_file_connectivity_tables(self):
        connectivity_tables = pd.read_excel(self.input_file, sheet_name='ConnectivityTables', header=0)
        return connectivity_tables

    def read_hspf_input_file_ftable(self):
        ftable = pd.read_excel(self.input_file, sheet_name='FTABLE', header=1)
        return ftable

    def read_hspf_input_file_hspf_impervious_cover(self):
        hspf_impervious_cover = pd.read_excel(self.input_file, sheet_name='HSPF Impervious Cover', header=0)
        hspf_impervious_cover_dict = self.dataframe_to_dict(hspf_impervious_cover, 'Code', ['Cover'])
        hspf_impervious_cover_id_dict = self.reverse_dict(hspf_impervious_cover_dict)
        return hspf_impervious_cover_dict, hspf_impervious_cover_id_dict

    def read_hspf_input_file_hspf_pervious_cover(self):
        hspf_pervious_cover = pd.read_excel(self.input_file, sheet_name='HSPF Pervious Cover', header=0)
        hspf_pervious_cover_dict = self.dataframe_to_dict(hspf_pervious_cover, 'Code', ['Cover'])
        hspf_pervious_cover_id_dict = self.reverse_dict(hspf_pervious_cover_dict)
        return hspf_pervious_cover_dict, hspf_pervious_cover_id_dict

    def read_hspf_input_file_hspf_soils(self):
        hspf_soils = pd.read_excel(self.input_file, sheet_name='HSPF Soils', header=0)
        hspf_soils_dict = self.dataframe_to_dict(hspf_soils, 'Code', ['Soil'])
        hspf_soils_id_dict = self.reverse_dict(hspf_soils_dict)
        return hspf_soils_dict , hspf_soils_id_dict

    def read_hspf_input_file_hspf_slope(self):
        hspf_slope = pd.read_excel(self.input_file, sheet_name='HSPF Slope', header=0)
        hspf_slope_dict = self.dataframe_to_dict(hspf_slope, 'Code', ['Slope'])
        hspf_slope_id_dict = self.reverse_dict(hspf_slope_dict)
        return hspf_slope_dict, hspf_slope_id_dict

    def read_hspf_input_file_overlay_base_codes(self):
        overlay_base_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Base_Codes', header=0)
        overlay_base_codes_dict = self.dataframe_to_dict(overlay_base_codes, 'Overlay', ['Base_Codes'])
        return overlay_base_codes_dict

    def read_hspf_input_file_overlay_perlnd_group_codes(self):
        overlay_other_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Perlnd_Group', header=0)
        overlay_other_codes_dict = self.dataframe_to_dict(overlay_other_codes, 'Overlay_Code', ['Base_Perlnd_Number', 'Description'])
        return overlay_other_codes_dict

    def read_hspf_input_file_overlay_soil_codes(self):
        overlay_soil_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Soils', header=0)
        overlay_soil_codes_dict = self.dataframe_to_dict(overlay_soil_codes, 'Overlay_Code', ['HSPF_Code', 'Description'])
        return overlay_soil_codes_dict

    def read_hspf_input_file_overlay_connectivity_codes(self):
        overlay_connectivity_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Connectivity', header=0)
        overlay_connectivity_codes_dict = self.dataframe_to_dict(overlay_connectivity_codes, 'Overlay_Code', ['Table_Number', 'Description'])
        return overlay_connectivity_codes_dict

    def read_hspf_input_file_overlay_land_use_codes(self):
        overlay_land_use_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Land_Use', header=0)
        overlay_land_use_codes_dict = self.dataframe_to_dict(overlay_land_use_codes, 'Overlay_Code', ['Description'])
        return overlay_land_use_codes_dict

    def read_hspf_input_file_overlay_impervious_cover_codes(self):
        overlay_impervious_cover_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Impervious_Cover', header=0)
        overlay_impervious_cover_codes_dict = self.dataframe_to_dict(overlay_impervious_cover_codes, 'Overlay_Code', ['HSPF_Code', 'Description'])
        return overlay_impervious_cover_codes_dict

    def read_hspf_input_file_overlay_pervious_cover_codes(self):
        overlay_pervious_cover_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Pervious_Cover', header=0)
        overlay_pervious_cover_codes_dict = self.dataframe_to_dict(overlay_pervious_cover_codes, 'Overlay_Code', ['HSPF_Code', 'Description'])
        return overlay_pervious_cover_codes_dict

    def read_hspf_input_file_overlay_slopes_codes(self):
        overlay_slopes_codes = pd.read_excel(self.input_file, sheet_name='Overlay_Slope', header=0)
        overlay_slopes_codes_dict = self.dataframe_to_dict(overlay_slopes_codes, 'Overlay_Code', ['HSPF_Code', 'Description'])
        return overlay_slopes_codes_dict

    def read_simulation_start_and_stop_dates(self):
        simulation_start_and_stop_dates = pd.read_excel(self.input_file, sheet_name='SimulationStartAndStopDates', header=0)
        hru_start_date = simulation_start_and_stop_dates.at[0, 'HRU']
        lumped_start_date = simulation_start_and_stop_dates.at[0, 'LUMPED']
        swmm_start_date = simulation_start_and_stop_dates.at[0, 'SWMM']
#        plot_start_date = simulation_start_and_stop_dates.at[0, 'PLOT']

        hru_stop_date = simulation_start_and_stop_dates.at[1, 'HRU']
        lumped_stop_date = simulation_start_and_stop_dates.at[1, 'LUMPED']
        swmm_stop_date = simulation_start_and_stop_dates.at[1, 'SWMM']
#        plot_stop_date = simulation_start_and_stop_dates.at[1, 'PLOT']
        return hru_start_date, swmm_start_date, lumped_start_date, hru_stop_date, swmm_stop_date, lumped_stop_date

    def read_scenario(self):
        simulation_and_post_processing = pd.read_excel(self.input_file, sheet_name='SimulationStartAndStopDates', header=0)
        scenario = simulation_and_post_processing.at[0, 'Scenario']
        return scenario

    def read_simulation_and_post_processing(self):
        simulation_and_post_processing = pd.read_excel(self.input_file, sheet_name='SimulationStartAndStopDates', header=0)
        run_hspf_swmm_model = simulation_and_post_processing.at[2, 'SWMM']
        run_lumped_model = simulation_and_post_processing.at[2, 'LUMPED']
        run_hspf_hru = simulation_and_post_processing.at[2, 'HRUOnly']

        post_process_swmm_model_statistics = simulation_and_post_processing.at[3, 'SWMM']
        post_process_lumped_model_statistics = simulation_and_post_processing.at[3, 'LUMPED']
        post_process_swmm_model_events = simulation_and_post_processing.at[4, 'SWMM']
        post_process_lumped_model_events = simulation_and_post_processing.at[4, 'LUMPED']


        write_swmm_to_dss = simulation_and_post_processing.at[5, 'SWMM']
        write_lumped_to_dss = simulation_and_post_processing.at[5, 'LUMPED']

        include_all_links = simulation_and_post_processing.at[6, 'SWMM']
        routing_time_step = simulation_and_post_processing.at[7, 'SWMM']

        return run_lumped_model, run_hspf_swmm_model, run_hspf_hru, \
               post_process_lumped_model_statistics, post_process_swmm_model_statistics,\
               post_process_lumped_model_events, post_process_swmm_model_events, \
               write_lumped_to_dss, write_swmm_to_dss,  \
               include_all_links,  routing_time_step

    def read_simulation_name_and_description(self):
        read_simulation_name_and_description = pd.read_excel(self.input_file, sheet_name='SimulationNameAndDescription', header=0)
        name = read_simulation_name_and_description['Simulation Name'].values[0]
        description = read_simulation_name_and_description['Description'].values[0]
        return name, description

    def read_precip_and_evap(self):
        precip_and_evap = pd.read_excel(self.input_file, sheet_name='PrecipAndEvap', header=0)
        rain_gage = int(precip_and_evap['Rain Gage'].values[0])
        rain_gage_multiplier = precip_and_evap['Rain Gage Multiplier'].values[0]
        pan_evap_evapotranspiration = precip_and_evap['Pan Evap to Evapotranspiration'].values[0]
        return rain_gage, rain_gage_multiplier, pan_evap_evapotranspiration

    def read_precip_and_evap_multiple_rain_gages(self):
        precip_and_evap = pd.read_excel(self.input_file, sheet_name='PrecipAndEvap', header=0)
        rain_gage = int(precip_and_evap['Rain Gage'].values[0])
        rain_gage_multiplier = precip_and_evap['Rain Gage Multiplier'].values[0]
        pan_evap_evapotranspiration = precip_and_evap['Pan Evap to Evapotranspiration'].values[0]
        return rain_gage, rain_gage_multiplier, pan_evap_evapotranspiration

    def read_events(self):
        events = pd.read_excel(self.input_file, sheet_name='Events', header=1).dropna(subset=['StartDate', 'EndDate'])
        return events

    def read_observed_and_simulation_data(self):
        read_observed_and_simulation_data = pd.read_excel(self.input_file, sheet_name='ObservedAndSimulatedData', header=0)
        read_observed_and_simulation_data = read_observed_and_simulation_data.dropna(subset=['Gage Location ID'])
        gage_location_id = read_observed_and_simulation_data['Gage Location ID'].astype(int, errors="ignore")
        swmm_link = read_observed_and_simulation_data['SWMM Link']
        try:
            lumped_model_rchres = read_observed_and_simulation_data['Lumped Model RCHRES'].values[0]
        except:
            print("could not read lumped model RCHRES")
            lumped_model_rchres = None
        locations_title_for_plots = read_observed_and_simulation_data['Location Title for Plots']
        return gage_location_id, swmm_link, lumped_model_rchres, locations_title_for_plots

    def read_to_dss(self):
        file_paths = pd.read_excel(self.input_file, sheet_name='ToDSS', header=0)
        links = file_paths['Links'].dropna().values
        nodes = file_paths['Nodes'].dropna().values
        if len(links) > 0:
            links = list(links)
        if len(nodes) > 0:
            nodes = list(nodes)
        return links, nodes

    def read_file_paths(self):
        file_paths = pd.read_excel(self.input_file, sheet_name='FilePaths', header=0)
        emgaats_model_folder = file_paths['Emgaats Model Folder'].values[0]
        win_hspf_lt_path = file_paths['WinHSPFLT EXE'].values[0]
        swmm_exe_path = file_paths['SWMM EXE'].values[0]
        observed_data_folder = file_paths['Observed Data Folder'].values[0]
        return emgaats_model_folder, win_hspf_lt_path, swmm_exe_path, observed_data_folder

    def dataframe_to_dict(self, df, key_column_name, value_column_names):
        keys = df[key_column_name].values
        if len(value_column_names) > 1:
            values = df[value_column_names].to_records(index=False)
        else:
            values = df[value_column_names[0]]
        dataframe_as_dict = dict(zip(keys, values))
        return dataframe_as_dict

    def dataframe_pair_of_columns_to_list_of_tuples(self, df, column_name, column_name_2):
        value1 = df[column_name].array
        value2 = df[column_name_2].array
        tuple = list(zip(value1, value2))
        return tuple

    @staticmethod
    def reverse_dict(dictionary):
        # TODO should move to utility class
        reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
        return reverse_dictionary