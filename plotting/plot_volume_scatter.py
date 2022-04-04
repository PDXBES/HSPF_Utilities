from plotting.plot_obs_sim_scatter import ObsSimScatterPlot


class VolumeScatterPlot(ObsSimScatterPlot):
    def __init__(self, begin_date, end_date, axs, observed_peak_flows, simulated_peak_flows,
                 volume_res=None, intercept=None):
        super(VolumeScatterPlot, self).__init__(begin_date, end_date, axs, observed_peak_flows, simulated_peak_flows)
        self.x_label = "Observed Volume [acft]"
        self.y_label = "Simulated Volume [acft]"
        self.res = volume_res
