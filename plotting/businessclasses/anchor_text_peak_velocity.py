from plotting.businessclasses.anchor_text_data import AnchorTextData

class AnchorTextPeakVelocity(AnchorTextData):
    def __init__(self, axs, observed_data=None, simulated_data=None):
        super(AnchorTextPeakVelocity, self).__init__(axs, observed_data, simulated_data)

    def _simulated_data_only_text(self, simulated_data):
        text = ""
        sim_velocity = simulated_data.peak_filtered_velocity(self.begin_date, self.end_date)
        sim_peak_velocity = "{:.{}f}".format(sim_velocity, self.precision)
        text += simulated_data.node_name + "\n" + "Peak Velocity [fps]: " + sim_peak_velocity + "\n"
        return text

    def _observed_data_only_text(self, observed_data):
        text = ""
        obs_velocity = observed_data.peak_filtered_velocity(self.begin_date, self.end_date)
        obs_peak_velocity = "{:.{}f}".format(obs_velocity, self.precision)
        text += observed_data.node_name + "\n" + "Peak Velocity [in]: " + obs_peak_velocity + "\n"
        return text

    def _simulated_and_observed_data_text(self, simulated_data, observed_data):
        text = ""
        obs_velocity = observed_data.peak_filtered_velocity(self.begin_date, self.end_date)
        sim_velocity = simulated_data.peak_filtered_velocity(self.begin_date, self.end_date)
        percent_difference_velocity = (sim_velocity - obs_velocity) / obs_velocity * 100

        obs_peak_velocity = "{:.{}f}".format(obs_velocity, self.precision)
        sim_peak_velocity = "{:.{}f}".format(sim_velocity, self.precision)
        perc_diff_velocity = "{:.{}f}".format(percent_difference_velocity, self.precision)
        text += observed_data.node_name + "\n" + "Peak Velocity [fps]: " + obs_peak_velocity + " " + sim_peak_velocity \
                + " " + perc_diff_velocity + "%\n"
        return text


