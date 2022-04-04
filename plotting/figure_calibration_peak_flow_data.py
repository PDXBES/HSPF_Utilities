
from plotting.plot_peak_flow_scatter import PeakFlowScatterPlot
from plotting.plot_volume_scatter import VolumeScatterPlot
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class CalibrationPeakFlowDataReview(object):
    def __init__(self, observed_peak_flows, simulated_peak_flows, observed_volumes, simulated_volumes,
                 peak_flow_res=None, volume_res=None, title=""):
        self.peak_flow_res = peak_flow_res
        self.volume_res = volume_res
        self.observed_peak_flows = observed_peak_flows
        self.simulated_peak_flows = simulated_peak_flows
        self.observed_volumes = observed_volumes
        self.simulated_volumes = simulated_volumes
        self.default_text_fontsize = 'xx-small'
        self.default_label_fontsize = 'x-small'
        self.default_title_fontsize = 'small'
        self.title = title
        self.flow_scatter_plot = None
        self.volume_scatter_plot = None
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

        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.9, top=0.7, bottom=0.3, hspace=0.0)
        ax_scatter_flow = self.fig.add_subplot(gs1[0, 0])

        gs2 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.9, top=0.7, bottom=0.3, hspace=0.0)
        ax_scatter_volume = self.fig.add_subplot(gs2[0, 1])

        self.flow_scatter_plot = PeakFlowScatterPlot(None, None, ax_scatter_flow, self.observed_peak_flows,
                                                     self.simulated_peak_flows, self.peak_flow_res)
        self.flow_scatter_plot.create_plot()

        self.volume_scatter_plot = VolumeScatterPlot(None, None, ax_scatter_volume, self.observed_volumes,
                                                     self.simulated_volumes, self.volume_res)
        self.volume_scatter_plot.create_plot()

    def show(self):
        plt.show()

    def write_to_pdf(self, pdf_file):
        pdf_file.savefig()
        #self.fig.savefig(pdf_file, format='pdf')

    def close(self):
        plt.close(self.fig)

