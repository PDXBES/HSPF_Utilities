from plotting.plot_obs_sim_scatter import ObsSimScatterPlot


class PeakFlowScatterPlot(ObsSimScatterPlot):
    def __init__(self, begin_date, end_date, axs, observed_peak_flows, simulated_peak_flows,
                 peak_flow_res=None):
        super(PeakFlowScatterPlot, self).__init__(begin_date, end_date, axs, observed_peak_flows, simulated_peak_flows)
        self.x_label = "Observed Peak Flow [cfs]"
        self.y_label = "Simulated Peak Flow [cfs]"
        self.res = peak_flow_res
