from plotting.plot import Plot
import matplotlib.pyplot as plt
import numpy as np
from plotting.businessclasses.anchor_text_peak_flow_and_volume import AnchorTextPeakFlowAndVolume


class FlowPlot(Plot):
    def __init__(self, begin_date, end_date, axs, temp_monitors=None, simulated_data_locations=None):
        super(FlowPlot, self).__init__(begin_date, end_date, axs)
        self.y_label = "Flow [cfs]"
        self.simulated_data_locations = simulated_data_locations
        self.temp_monitors = temp_monitors
        self.peak_flow_and_volume = AnchorTextPeakFlowAndVolume(self.axs, self.temp_monitors, self.simulated_data_locations)

    def create_plot(self):
        if self.simulated_data_locations is not None:
            for simulated_data in self.simulated_data_locations:
                sim_data = simulated_data.flow_data[simulated_data.flow_data.columns[0]]
                sim_name = str(simulated_data.link_name) + ' sim'
                sim_dates = simulated_data.flow_data.index.values
                line, = self.axs.plot(sim_dates, sim_data, '-', label=sim_name, linewidth=1, color='r')
                self.plot_curves.append(line)

        if self.temp_monitors is not None:
            for temp_monitor in self.temp_monitors:

                raw_data = temp_monitor.flow_data[temp_monitor.flow_data.columns[0]]
                raw_name = temp_monitor.node_name + ' raw'
                raw_dates = temp_monitor.flow_data.index.values
                line, = self.axs.plot(raw_dates, raw_data, '-', label=raw_name, linewidth=.2, color='y')
                self.plot_curves.append(line)

                filtered_data = temp_monitor.filtered_flow_data[temp_monitor.filtered_flow_data.columns[0]]
                filtered_name = temp_monitor.node_name + ' filtered'
                filtered_dates = temp_monitor.filtered_flow_data.index.values
                line, = self.axs.plot(filtered_dates, filtered_data, '-', label=filtered_name, linewidth=.5, color='b')
                self.plot_curves.append(line)

        self.add_legend()
        self.axs.set_ylabel(self.y_label)
        self.axs.set_xlim(self.begin_date, self.end_date)
        self.axs.get_xaxis().set_visible(False)
        self.peak_flow_and_volume.add_anchor_text()
        return self.axs

    def add_upload_dates(self, temp_monitor):
        values = temp_monitor.number_of_upload_dates() * [0]
        upload_dates = temp_monitor.upload_dates()
        line, = self.axs.plot(upload_dates, values, '-x', label=temp_monitor.node_name + ' uploads',
                              markersize=10, linewidth=0.1)
        self.plot_curves.append(line)
