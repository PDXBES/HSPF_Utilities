from plotting.plot import Plot
import matplotlib.pyplot as plt
import numpy as np
from plotting.businessclasses.anchor_text_peak_flow_and_volume import AnchorTextPeakFlowAndVolume


class TotalVolumeBarChartPlot(Plot):
    def __init__(self, begin_date, end_date, axs, observed_total_volumes, simulated_total_volumes, date_labels, percent_difference_labels):
        super(TotalVolumeBarChartPlot, self).__init__(begin_date, end_date, axs)
        self.observed_total_volumes = observed_total_volumes
        self.simulated_total_volumes = simulated_total_volumes
        self.date_labels = date_labels
        self.percent_difference_labels = percent_difference_labels
        self.ylabel = "Volume [acre-ft]"

    def create_plot(self):
        x = np.arange(len(self.observed_total_volumes))
        self.axs.bar(x + 0.00, self.observed_total_volumes, color='b', width=0.25)
        bars = self.axs.bar(x + 0.25, self.simulated_total_volumes, color='g', width=0.25)
        self.axs.set_ylabel(self.ylabel)
        if self.percent_difference_labels is not None:
            self.axs.bar_label(bars, labels=self.percent_difference_labels, rotation=45, fontsize=4) #fontsize=6, padding=4,
        self.axs.set_xticks(x)
        self.axs.set_xticklabels(list(self.date_labels), rotation=45)
        self.axs.legend(labels=['OBS', 'SIM'])
        return self.axs
