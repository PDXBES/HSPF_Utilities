from plotting.businessclasses.anchor_text_data import AnchorTextData
import math

class AnchorTextPeakFlowAndVolume(AnchorTextData):
    def __init__(self, axs, observed_data=None, simulated_data=None):
        super(AnchorTextPeakFlowAndVolume, self).__init__(axs, observed_data, simulated_data)

    def _simulated_data_only_text(self, simulated_data):
        text = ""
        sim_peak_flow = "{:.{}f}".format(simulated_data.peak_filtered_flow(self.begin_date, self.end_date), self.precision)
        sim_volume = "{:.{}f}".format(simulated_data.filtered_volume(self.begin_date, self.end_date), self.precision)
        text += simulated_data.node_name + "\n" + "Peak Flow [cfs]: " + sim_peak_flow + "\n" + "Volume [acft]: " + sim_volume + "\n"
        return text

    def _observed_data_only_text(self, observed_data):
        text = ""
        obs_peak_flow = "{:.{}f}".format(observed_data.peak_filtered_flow(self.begin_date, self.end_date), self.precision)
        obs_volume = "{:.{}f}".format(observed_data.filtered_volume(self.begin_date, self.end_date), self.precision)
        text += observed_data.node_name + "\n" + "Peak Flow [cfs]: " + obs_peak_flow + "\n" + "Volume [acft]: " + obs_volume + "\n"
        return text

    def _simulated_and_observed_data_text(self, simulated_data, observed_data):
        text = ""
        obs_flow = observed_data.peak_filtered_flow(self.begin_date, self.end_date)
        sim_flow = simulated_data.peak_filtered_flow(self.begin_date, self.end_date)
        if obs_flow != 0:
            percent_difference_flow = (sim_flow - obs_flow) / obs_flow * 100
        else:
            percent_difference_flow = math.nan

        obs_volume = observed_data.filtered_volume(self.begin_date, self.end_date)
        sim_volume = simulated_data.filtered_volume(self.begin_date, self.end_date)
        if obs_volume > 0:
            percent_difference_volume = (sim_volume - obs_volume) / obs_volume * 100
        else:
            percent_difference_volume = math.nan

        obs_peak_flow = "{:.{}f}".format(obs_flow, self.precision)
        sim_peak_flow = "{:.{}f}".format(sim_flow, self.precision)
        obs_vol = "{:.{}f}".format(obs_volume, self.precision)
        sim_vol = "{:.{}f}".format(sim_volume, self.precision)
        perc_diff_flow = "{:.{}f}".format(percent_difference_flow, self.precision)
        perc_diff_vol = "{:.{}f}".format(percent_difference_volume, self.precision)
        text += observed_data.node_name + "\n" + "Peak Flow [cfs]: " + obs_peak_flow + " " + sim_peak_flow \
                + " " + perc_diff_flow + "%\n" + \
                "Volume [acft]: " + obs_vol + " " + sim_vol \
                + " " + perc_diff_vol + "%\n"
        return text


