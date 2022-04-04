from plotting.businessclasses.anchor_text_data import AnchorTextData

class AnchorTextPeakDepth(AnchorTextData):
    def __init__(self, axs, observed_data=None, simulated_data=None):
        super(AnchorTextPeakDepth, self).__init__(axs, observed_data, simulated_data)

    def _simulated_data_only_text(self, simulated_data):
        text = ""
        sim_depth = simulated_data.peak_filtered_depth(self.begin_date, self.end_date)
        sim_peak_depth = "{:.{}f}".format(sim_depth, self.precision)
        text += simulated_data.node_name + "\n" + "Peak Depth [in]: " + sim_peak_depth + "\n"
        return text

    def _observed_data_only_text(self, observed_data):
        text = ""
        obs_depth = observed_data.peak_filtered_depth(self.begin_date, self.end_date)
        obs_peak_depth = "{:.{}f}".format(obs_depth, self.precision)
        text += observed_data.node_name + "\n" + "Peak Depth [in]: " + obs_peak_depth + "\n"
        return text

    def _simulated_and_observed_data_text(self, simulated_data, observed_data):
        text = ""
        obs_depth = observed_data.peak_filtered_depth(self.begin_date, self.end_date)
        sim_depth = simulated_data.peak_filtered_depth(self.begin_date, self.end_date)
        percent_difference_depth = (sim_depth - obs_depth) / obs_depth * 100

        obs_peak_depth = "{:.{}f}".format(obs_depth, self.precision)
        sim_peak_depth = "{:.{}f}".format(sim_depth, self.precision)
        perc_diff_depth = "{:.{}f}".format(percent_difference_depth, self.precision)
        text += observed_data.node_name + "\n" + "Peak Depth [in]: " + obs_peak_depth + " " + sim_peak_depth \
                + " " + perc_diff_depth + "%\n"
        return text


