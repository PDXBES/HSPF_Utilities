from plotting.plot import Plot
from plotting.businessclasses.anchor_text_peak_depth import AnchorTextPeakDepth


class FlowScatterPlot(Plot):
    def __init__(self, begin_date, end_date, axs, temp_monitors=None, simulated_data_locations=None):
        super(FlowScatterPlot, self).__init__(begin_date, end_date, axs)
        self.x_label = "Flow [cfs]"
        self.y_label = "Depth [inch]"
        self.simulated_data = simulated_data_locations
        self.temp_monitors = temp_monitors
        self.peak_depth = AnchorTextPeakDepth(self.axs, self.temp_monitors, self.simulated_data)

    def create_plot(self):
        for temp_monitor in self.temp_monitors:
            self.axs.scatter(temp_monitor.filtered_flow_data, temp_monitor.filtered_depth_data, c='b')
            self.axs.set_xlabel(self.x_label)
            self.axs.set_ylabel(self.y_label)

    def update_scatter_plot(self, begin_date, end_date):
        self.axs.clear()
        self.create_plot()
        for temp_monitor in self.temp_monitors:
            subdepth = temp_monitor.filtered_depth_data.loc[begin_date:end_date]
            subflow = temp_monitor.filtered_flow_data.loc[begin_date:end_date]
            self.axs.scatter(subflow, subdepth, c='r')
