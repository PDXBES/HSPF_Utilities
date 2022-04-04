from plotting.plot import Plot
from plotting.businessclasses.anchor_text_peak_velocity import AnchorTextPeakVelocity


class VelocityPlot(Plot):
    def __init__(self, begin_date, end_date, axs, temp_monitors=None, simulated_data_locations=None):
        super(VelocityPlot, self).__init__(begin_date, end_date, axs)
        self.y_label = "Velocity [fps]"
        self.simulated_data = simulated_data_locations
        self.temp_monitors = temp_monitors
        self.peak_velocity = AnchorTextPeakVelocity(self.axs, self.temp_monitors, self.simulated_data)

    def create_plot(self):
        for temp_monitor in self.temp_monitors:
            raw_data = temp_monitor.velocity_data[temp_monitor.velocity_data.columns[0]]
            raw_name = temp_monitor.node_name + ' raw'
            raw_dates = temp_monitor.velocity_data.index.values
            line, = self.axs.plot(raw_dates, raw_data, '-', label=raw_name, markersize=1)
            self.plot_curves.append(line)

            filtered_data = temp_monitor.filtered_velocity_data[temp_monitor.filtered_velocity_data.columns[0]]
            filtered_name = temp_monitor.node_name + ' filtered'
            filtered_dates = temp_monitor.filtered_velocity_data.index.values
            line, = self.axs.plot(filtered_dates, filtered_data, '-', label=filtered_name, markersize=1, linewidth=0.5)
            self.plot_curves.append(line)
            self.add_upload_dates(temp_monitor)
        self.peak_velocity.add_anchor_text()
        self.add_legend()
        self.axs.set_ylabel(self.y_label)
        self.axs.set_xlim(self.begin_date, self.end_date)
        self.axs.get_xaxis().set_visible(True)
        return self.axs

    def add_upload_dates(self, temp_monitor):
        values = temp_monitor.number_of_upload_dates() * [0]
        upload_dates = temp_monitor.upload_dates()
        line, = self.axs.plot(upload_dates, values, '-x', label=temp_monitor.node_name + ' uploads',
                              markersize=10, linewidth=0.1)
        self.plot_curves.append(line)
