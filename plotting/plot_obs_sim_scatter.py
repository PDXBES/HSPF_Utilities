from plotting.plot import Plot
import numpy as np
import math

class ObsSimScatterPlot(Plot):
    def __init__(self, begin_date, end_date, axs, observed_data, simulated_data, res=None):
        super(ObsSimScatterPlot, self).__init__(begin_date, end_date, axs)
        self.x_label = None
        self.y_label = None
        self.observed_data = observed_data
        self.simulated_data = simulated_data
        self.res = res

    def r2_text(self):
        if self.res is not None:
            x = self.max_value_of_data_for_axis()*.6
            y = self.max_value_of_data_for_axis()*.2

            r2 = "y = " + f"{self.res.slope:.2f}" + "*x" + " + " + f"{self.res.intercept:.2f}" + "\n" + f"R^2: {self.res.rvalue**2:.2f}"
            self.axs.text(x, y, r2, fontsize=6)
            line = np.asarray([np.amin(self.observed_data), np.amax(self.observed_data)])
            self.axs.plot(line, self.res.intercept + self.res.slope * line,
                          'r:', label='fitted line')

    def max_value_of_data_for_axis(self):
        obs_max = np.amax(self.observed_data)
        sim_max = np.amax(self.simulated_data)
        if obs_max > sim_max and not math.isnan(obs_max):
            max_flow = obs_max
        elif not math.isnan(sim_max):
            max_flow = sim_max
        else:
            max_flow = 0
        if max_flow > 10:
            max_flow = math.ceil(max_flow/10) * 10
        else:
            max_flow = math.ceil(max_flow)
        return max_flow

    def create_plot(self):
        self.axs.scatter(self.observed_data, self.simulated_data, c='b')
        x = [0, self.max_value_of_data_for_axis()]
        y = [0, self.max_value_of_data_for_axis() * 1.25]
        self.axs.plot(x, y, '-', linewidth=1)
        x = [0, self.max_value_of_data_for_axis()]
        y = [0, self.max_value_of_data_for_axis()]
        self.axs.plot(x, y, '-', linewidth=1)
        x = [0, self.max_value_of_data_for_axis()]
        y = [0, self.max_value_of_data_for_axis() * .75]
        self.axs.plot(x, y, '-', linewidth=1)
        self.axs.set_xlabel(self.x_label)
        self.axs.set_ylabel(self.y_label)
        self.axs.set_xlim(0, self.max_value_of_data_for_axis())
        self.axs.set_ylim(0, self.max_value_of_data_for_axis())
        self.r2_text()
