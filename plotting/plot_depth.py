from plotting.plot import Plot
from plotting.businessclasses.anchor_text_peak_depth import AnchorTextPeakDepth


class DepthPlot(Plot):
    def __init__(self, begin_date, end_date, axs, temp_monitors=None, simulated_data_locations=None):
        super(DepthPlot, self).__init__(begin_date, end_date, axs)
        self.y_label = "Depth [in]"
        self.simulated_data = simulated_data_locations
        self.temp_monitors = temp_monitors
        self.peak_depth = AnchorTextPeakDepth(self.axs, self.temp_monitors, self.simulated_data)

    def create_plot(self):
        for temp_monitor in self.temp_monitors:
            raw_data = temp_monitor.depth_data[temp_monitor.depth_data.columns[0]]
            raw_name = temp_monitor.node_name + ' raw'
            raw_dates = temp_monitor.depth_data.index.values
            line, = self.axs.plot(raw_dates, raw_data, '-', label=raw_name, markersize=1)
            self.plot_curves.append(line)

            filtered_data = temp_monitor.filtered_depth_data[temp_monitor.filtered_depth_data.columns[0]]
            filtered_name = temp_monitor.node_name + ' filtered'
            filtered_dates = temp_monitor.filtered_depth_data.index.values
            line, = self.axs.plot(filtered_dates, filtered_data, '-', label=filtered_name, markersize=1, linewidth=0.5)
            self.plot_curves.append(line)
            self.add_upload_dates(temp_monitor)
        self.peak_depth.add_anchor_text()
        self.add_legend()
        self.axs.set_ylabel(self.y_label)
        self.axs.set_xlim(self.begin_date, self.end_date)
        self.axs.get_xaxis().set_visible(False)
        return self.axs

    def add_upload_dates(self, temp_monitor):
        try:
            values = temp_monitor.number_of_upload_dates() * [0]
            upload_dates = temp_monitor.upload_dates()
            line, = self.axs.plot(upload_dates, values, '-x', label=temp_monitor.node_name + ' uploads',
                                  markersize=10, linewidth=0.1)
            self.plot_curves.append(line)
        except:
            pass #TODO fix this for USGS data
