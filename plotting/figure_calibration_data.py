from plotting.plot_precipitation import PrecipitationPlot
from plotting.plot_flow import FlowPlot
from plotting.plot_depth import DepthPlot
from plotting.plot_flow_scatter import FlowScatterPlot
from flow_data.businessclasses.temporary_flow_monitor_data import ObservedData
from met_data.businessclasses.precipitation_gage import PrecipitationGage
import matplotlib.pyplot as plt
import matplotlib.dates as dates1
from pandas.plotting import register_matplotlib_converters
from datetime import datetime
from datetime import timedelta
from flow_data.businessclasses.simulated_data import SimulatedData
register_matplotlib_converters()
import matplotlib.style as mplstyle
mplstyle.use('fast')


class CalibrationDataReview(object):
    def __init__(self, begin, end, precipitation_gages, monitor_data_sets, simulated_data_sets,
                 scatter_plots=False, depth_plot=False, title="", peak_flow=None):
        self.title = title
        self.scatter_plots = scatter_plots
        self.depth_plots = depth_plot
        self.precipitation_gages = precipitation_gages
        self.monitor_data_sets = monitor_data_sets
        self.simulated_data_sets = simulated_data_sets
        if monitor_data_sets is None and simulated_data_sets is not None:
            self.flow = True
        else:
            self.flow = monitor_data_sets[0].flow
        if monitor_data_sets is None and simulated_data_sets is not None:
            self.velocity = False
        else:
            self.velocity = monitor_data_sets[0].velocity
        self.depth = False

        self.begin = begin
        self.end = end
        self.fig = None
        self.default_text_fontsize = 'xx-small'
        self.default_label_fontsize = 'x-small'
        self.default_title_fontsize = 'small'
        self.precipitation_plot = None
        self.flow_plot = None
        self.depth_plot = None
        self.flow_scatter_plot = None
        self.fig = None

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.xlim_beg_orig = None
        self.xlim_end_orig = None
        self.ylim_beg_orig = None
        self.ylim_end_orig = None
        self.timestep_forward = None
        self.timestep_backward = None
        self.timestep_name = None
        self.peak_flow = peak_flow

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
        gs4 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.90, top=.9, bottom=0.70, hspace=0.0)
        ax_precip = self.fig.add_subplot(gs4[0, 0])

        gs3 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.90, top=0.7, bottom=0.1, hspace=0.0)
        ax_flow = self.fig.add_subplot(gs3[0, 0], sharex=ax_precip)

        if self.depth_plot:
            gs2 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.60, top=0.4, bottom=0.1, hspace=0.0)
            ax_depth = self.fig.add_subplot(gs2[0, 0], sharex=ax_precip)

        if self.scatter_plots:
            gs1 = self.fig.add_gridspec(nrows=2, ncols=1, left=0.7, right=0.95, top=.9, bottom=0.1, hspace=0.2)
            ax_scatter_flow = self.fig.add_subplot(gs1[0, 0])

        self.precipitation_plot = PrecipitationPlot(self.begin, self.end, self.precipitation_gages, ax_precip)
        self.precipitation_plot.create_plot()

        if self.flow:
            self.flow_plot = FlowPlot(self.begin, self.end, ax_flow, self.monitor_data_sets, self.simulated_data_sets)
            self.flow_plot.create_plot()
            if not self.depth_plot:
                self.flow_plot.xaxis_visible()
            if self.peak_flow is not None:
                self.flow_plot.axs.set_ylim(0, self.peak_flow)

        if self.depth_plot:
            self.depth_plot = DepthPlot(self.begin, self.end, ax_depth, self.monitor_data_sets, self.simulated_data_sets)
            self.depth_plot.create_plot()
            self.depth_plot.xaxis_visible()

        if self.scatter_plots:
            self.flow_scatter_plot = FlowScatterPlot(self.begin, self.end, ax_scatter_flow, [self.monitor_data_sets])
            self.flow_scatter_plot.create_plot()

        # self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.precipitation_plot.axs.callbacks.connect('xlim_changed', self.onzoom)
        if self.flow:
            self.flow_plot.axs.callbacks.connect('xlim_changed', self.onzoom)
        if self.depth:
            self.depth_plot.axs.callbacks.connect('xlim_changed', self.onzoom)

        self.fig.autofmt_xdate()

    def show(self):
        plt.show()

    def write_to_pdf(self, pdf_file):
        pdf_file.savefig()
        #self.fig.savefig(pdf_file, format='pdf')

    def close(self):
        plt.close(self.fig)

    def onzoom(self, event):
        a = event.axes

        beg_num, end_num = a.get_xlim()
        beg_date = dates1.num2date(beg_num, tz=None)
        end_date = dates1.num2date(end_num, tz=None)
        end_date.replace(tzinfo=None)
        beg_date.replace(tzinfo=None)
        beg_date = beg_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=None)
        self.precipitation_plot.peak_and_total_precip.update_anchor_text(beg_date, end_date)
        if self.flow:
            print("flow")
            self.flow_plot.peak_flow_and_volume.update_anchor_text(beg_date, end_date)
        if self.depth:
            self.depth_plot.peak_filtered_depth.update_anchor_text(beg_date, end_date)
        if self.flow and self.depth:
            self.flow_scatter_plot.update_scatter_plot(beg_date, end_date)

        self.fig.canvas.draw_idle()

    def onpick(self, event):
        if event.artist is not None:
            if event.artist in self.precipitation_plot.lined.keys():
                self.precipitation_plot.data_set_visibility(event)
            elif event.artist in self.flow_plot.lined.keys():
                self.flow_plot.data_set_visibility(event)
            elif event.artist in self.depth_plot.lined.keys():
                self.depth_plot.data_set_visibility(event)

        self.fig.canvas.draw_idle()

    # def press(self, event):
    #     print('press', event.key)
    #     if event.key in ('left', 'right', 'h', 'd', 'w', 'm', 'y', 'a', 'e', 'H', 'D', 'W', 'M', 'Y'):
    #         xlim_beg, xlim_end = self.depth_plot.axs.get_xlim()
    #         ylim_beg, ylim_end = self.depth_plot.axs.get_ylim()
    #         if self.x1 == None and self.x2 == None and self.y1 == None and self.y2 == None:
    #             #Set all values on first time using this routine
    #             #self.xlim_beg_orig = xlim_beg
    #             #self.xlim_end_orig = xlim_end
    #             #self.ylim_beg_orig = ylim_beg
    #             #self.ylim_end_orig = ylim_end
    #             self.x1 = xlim_beg
    #             self.x2 = xlim_end
    #             self.y1 = ylim_beg
    #             self.y2 = ylim_end
    #         elif xlim_beg == self.x1 or xlim_end == self.x2 or\
    #            ylim_beg == self.y1 or ylim_end == self.y2:
    #             #Reset all values on when lim_beg_orig and lim are the same
    #             #self.xlim_beg_orig = xlim_beg
    #             #self.xlim_end_orig = xlim_end
    #             #self.ylim_beg_orig = ylim_beg
    #             #self.ylim_end_orig = ylim_end
    #             self.x1 = xlim_beg
    #             self.x2 = xlim_end
    #             self.y1 = ylim_beg
    #             self.y2 = ylim_end
    #         elif (xlim_beg == self.x1 or xlim_end == self.x2) and (ylim_beg != self.y1 or ylim_end != self.y2):
    #             #Reset y if only y axis has changed
    #             self.x1 = xlim_beg
    #             self.x2 = xlim_end
    #             self.y1 = ylim_beg
    #             self.y2 = ylim_end
    #     if event.key in ('h', 'd', 'w', 'm', 'y', 'a', 'e' 'H', 'D', 'W', 'M', 'Y'):
    #         self.timestep_name = event.key
    #         print("Timestep: " + self.timestep_name)
    #     if event.key in ('left', 'right'):
    #         if self.timestep_name == 'h':
    #             self.timestep_forward = timedelta(hours=1)
    #             self.timestep_backward = timedelta(hours=1)
    #         elif self.timestep_name == 'd':
    #             self.timestep_forward = timedelta(days=1)
    #             self.timestep_backward = timedelta(days=1)
    #         elif self.timestep_name == 'w':
    #             self.timestep_forward = timedelta(weeks=1)
    #             self.timestep_backward = timedelta(weeks=1)
    #         elif self.timestep_name in ('m', 'y'):
    #             beg_date = dates1.num2date(self.x1)
    #             Y = beg_date.year
    #             M = beg_date.month
    #             D = 1#beg_date.day
    #             h = 0#beg_date.hour
    #             m = 0#beg_date.minute
    #             s = 0#beg_date.second
    #             ms = 0#beg_date.microsecond
    #             offset = beg_date.tzinfo
    #             print(beg_date)
    #             if self.timestep_name == 'm':
    #                 if M == 12:
    #                     Y_forward = Y + 1
    #                     M_forward = 1
    #                     M_backward = 11
    #                     Y_backward = Y
    #                 elif M == 1:
    #                     Y_forward = Y
    #                     Y_backward = Y - 1
    #                     M_forward = 2
    #                     M_backward = 12
    #                 else:
    #                     Y_forward = Y
    #                     Y_backward = Y
    #                     M_forward = M + 1
    #                     M_backward = M - 1
    #                 end_date_forward = datetime(Y_forward, M_forward, D, h, m, s, ms, offset)
    #                 end_date_backward = datetime(Y_backward, M_backward, D, h, m, s, ms, offset)
    #                 print(end_date_forward)
    #                 print(end_date_backward)
    #                 print(self.x1)
    #                 self.timestep_forward = end_date_forward - beg_date
    #                 self.timestep_backward = beg_date - end_date_backward
    #             elif self.timestep_name == 'y':
    #                 Y_forward = Y + 1
    #                 Y_backward = Y - 1
    #                 end_date_forward = datetime(Y_forward, M, D, h, m, s, ms, offset)
    #                 end_date_backward = datetime(Y_backward, M, D, h, m, s, ms, offset)
    #                 self.timestep_forward = end_date_forward - beg_date
    #                 self.timestep_backward = beg_date - end_date_backward
    #         elif self.timestep_name == 'a':
    #             pass
    #         elif self.timestep_name == 'e':
    #             pass
    #             print(self.timestep_forward)
    #             print(self.timestep_backward)
    #     elif self.timestep_name in ('H', 'D', 'W', 'M', 'Y'):
    #         pass
    #     if event.key == 'left':
    #         print("back")
    #         self.x2 = self.x1 - self.timestep_backward.total_seconds()/(3600*24)
    #         self.x1 = self.x2 - self.timestep_backward.total_seconds()/(3600*24)
    #         self.depth_plot.axs.axis([self.x1, self.x2, self.y1, self.y2])
    #         self.fig.canvas.draw_idle()
    #     if event.key == 'right':
    #         print("forward")
    #         self.x1 = self.x1 + self.timestep_forward.total_seconds()/(3600*24)
    #         self.x2 = self.x2 + self.timestep_forward.total_seconds()/(3600*24)
    #         self.depth_plot.axs.axis([self.x1, self.x2, self.y1, self.y2])
    #         self.fig.canvas.draw_idle()
