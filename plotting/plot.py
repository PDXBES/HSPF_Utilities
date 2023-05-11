import warnings
warnings.filterwarnings("ignore")


class Plot(object):
    def __init__(self, begin_date, end_date, axs):
        self.begin_date = begin_date
        self.end_date = end_date
        self.axs = axs
        self.xlabel = None
        self.ylabel = None
        self.title = None
        self.legend_lines_and_plot_curves = None
        self.plot_curves = []
        self.legend = None

    def create_plot(self):
        return self.axs

    def add_legend(self):
        self.legend = self.axs.legend(loc='upper left', fancybox=False, shadow=False)
        self.legend.get_frame().set_alpha(0.4)
        self.lined = dict()
        for legline, origline in zip(self.legend.get_lines(), self.plot_curves):
            legline.set_picker(5)  # 5 pts tolerance
            self.lined[legline] = origline

    def xaxis_visible(self):
        self.axs.get_xaxis().set_visible(True)

    def xaxis_not_visible(self):
        self.axs.get_xaxis().set_visible(False)

    def yaxis_autoscale_on(self):
        self.axs.autoscale(enable=True, axis='y')

    def yaxis_autoscale_off(self):
        self.axs.autoscale(enable=False, axis='y')

    def yaxis_autoscale_switch(self):
        autoscale = not self.axs.get_autoscalex_on(self)
        self.axs.autoscale(enable=autoscale, axis='y')

    def data_set_visibility(self, event):
        legend_line = event.artist
        plot_curve = self.lined[legend_line]
        visible = not plot_curve.get_visible()
        plot_curve.set_visible(visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if visible:
            legend_line.set_alpha(1.0)
        else:
            legend_line.set_alpha(0.2)