from plotting.plot import Plot
import matplotlib.pyplot as plt
import numpy as np
from plotting.businessclasses.anchor_text_peak_flow_and_volume import AnchorTextPeakFlowAndVolume


class MonthlyFlowBarChartPlot(Plot):
    def __init__(self, begin_date, end_date, axs, observed_monthly_flows, simulated_monthly_flows, date_labels):
        super(MonthlyFlowBarChartPlot, self).__init__(begin_date, end_date, axs)
        self.observed_monthly_flows = observed_monthly_flows
        self.simulated_monthly_flows = simulated_monthly_flows
        self.date_labels = date_labels
        self.ylabel = "Average Flow [cfs]"

    def create_plot(self):
        x = np.arange(len(self.observed_monthly_flows))
        self.axs.bar(x + 0.00, self.observed_monthly_flows, color='b', width=0.25)
        self.axs.bar(x + 0.25, self.simulated_monthly_flows, color='g', width=0.25)
        self.axs.set_ylabel(self.ylabel)
        self.axs.set_xticks(x)
        self.axs.set_xticklabels(list(self.date_labels), rotation=45)
        self.axs.legend(labels=['OBS', 'SIM'])
        return self.axs
