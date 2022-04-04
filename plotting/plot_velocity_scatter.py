from plotting.plot import Plot
from plotting.businessclasses.anchor_text_peak_depth import AnchorTextPeakDepth


class VelocityScatterPlot(Plot):
    def __init__(self, begin_date, end_date, axs, temp_monitors=None, simulated_data_locations=None):
        super(VelocityScatterPlot, self).__init__(begin_date, end_date, axs)
        self.x_label = "Velocity [fps]"
        self.y_label = "Depth [inch]"
        self.simulated_data = simulated_data_locations
        self.temp_monitors = temp_monitors
        self.peak_depth = AnchorTextPeakDepth(self.axs, self.temp_monitors, self.simulated_data)

    def create_plot(self):
        for temp_monitor in self.temp_monitors:
            self.axs.scatter(temp_monitor.filtered_velocity_data, temp_monitor.filtered_depth_data, c='b')
            self.axs.set_xlabel(self.x_label)
            self.axs.set_ylabel(self.y_label)

    def update_scatter_plot(self, begin_date, end_date):
        self.axs.clear()
        self.create_plot()
        for temp_monitor in self.temp_monitors:
            subdepth = temp_monitor.filtered_depth_data.loc[begin_date:end_date]
            subvelocity = temp_monitor.filtered_velocity_data.loc[begin_date:end_date]
            self.axs.scatter(subvelocity, subdepth, c='r')

