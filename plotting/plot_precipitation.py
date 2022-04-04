from plotting.plot import Plot
from plotting.businessclasses.anchor_text_peak_and_total_precip import AnchorTextPeakAndTotalPrecip

class PrecipitationPlot(Plot):
    def __init__(self, begin_date, end_date, precipitation_gages, axs):
        super(PrecipitationPlot, self).__init__(begin_date, end_date, axs)
        self.precipitation_gages = precipitation_gages
        self.y_label = "Precip [in]"
        self.timestep = None
        self.peak_and_total_precip = AnchorTextPeakAndTotalPrecip(self.axs, precipitation_gages)

    def create_plot(self):
        colors = ['r', 'g', 'b', 'c', 'y']
        for precipitation_gage, color in zip(self.precipitation_gages, colors):
            gage_name = "RG" + str(precipitation_gage.h2_number)
            subprec = precipitation_gage.filled_data.loc[self.begin_date:self.end_date]
            dates = subprec.index.values
            precip = subprec[subprec.columns[0]]
            self.axs.set_ylim(.3, 0)
            line_collection = self.axs.vlines(dates, [0], precip, color=color, label=gage_name)
            self.plot_curves.append(line_collection)
        self.peak_and_total_precip.add_anchor_text()
        self.add_legend()
        self.axs.set_title(self.title)
        self.axs.set_ylabel(self.y_label)
        self.xaxis_not_visible()
        self.beg_num, self.end_num = self.axs.get_xlim()
        return self.axs

    def update_plot(self):
        self.axs.set_xlim(self.beg_num, self.end_num)