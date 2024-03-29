
from plotting.plot_total_volume_bar_chart import TotalVolumeBarChartPlot
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class TotalVolumeFlowBarChart(object):
    def __init__(self, observed_total_volume, simulated_total_volume, date_labels, percent_difference_labels=None, title=""):
        self.percent_difference_labels = percent_difference_labels
        self.observed_total_volume = observed_total_volume
        self.simulated_total_volume = simulated_total_volume
        self.total_volume_flow_bar_chart_plot = None
        self.date_labels = date_labels
        self.default_text_fontsize = 'xx-small'
        self.default_label_fontsize = 'x-small'
        self.default_title_fontsize = 'small'
        self.title = title
        self.fig = None

    def set_figure_format_params(self):
        plt.rcParams['legend.title_fontsize'] = self.default_text_fontsize
        plt.rcParams['legend.fontsize'] = self.default_text_fontsize
        plt.rcParams['axes.labelsize'] = self.default_label_fontsize
        plt.rcParams['axes.titlesize'] = self.default_title_fontsize
        plt.rcParams['figure.titlesize'] = self.default_title_fontsize
        plt.rcParams['xtick.labelsize'] = self.default_text_fontsize
        plt.rcParams['ytick.labelsize'] = self.default_text_fontsize

    def create_figure(self):
        self.set_figure_format_params()
        self.fig = plt.figure(constrained_layout=False)
        self.fig.suptitle(self.title)

        gs1 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.0)
        ax_average_flow = self.fig.add_subplot(gs1[0, 0])

        self.total_volume_flow_bar_chart_plot = TotalVolumeBarChartPlot(None, None,
                                                                        ax_average_flow,
                                                                        self.observed_total_volume,
                                                                        self.simulated_total_volume,
                                                                        self.date_labels,
                                                                        self.percent_difference_labels)
        self.total_volume_flow_bar_chart_plot.create_plot()

    def show(self):
        plt.show()

    def write_to_pdf(self, pdf_file):
        pdf_file.savefig()

    def close(self):
        plt.close(self.fig)

