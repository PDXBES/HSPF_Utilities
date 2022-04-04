from matplotlib.offsetbox import AnchoredText
import matplotlib.dates as dates

class AnchorTextData(object):
    def __init__(self, axs, observed_data=None, simulated_data=None):
        self.observed_data_sets = observed_data
        self.simulated_data_sets = simulated_data
        self.simulated_and_observed_data_sets = None
        self.anchor_text = None
        self.begin_date = None
        self.end_date = None
        self.axs = axs
        self.precision = 1
        self.observed_data_header = ""
        self.simulated_data_header = ""
        self.simulated_and_observed_data_header = ""

    @property
    def _simulated_data(self):
        return not self.simulated_data_sets == None

    @property
    def _observed_data(self):
        return not self.observed_data_sets == None

    def _observed_and_simulated_data(self):
        if not self._simulated_data and not self._observed_data:
            raise Exception
        elif self._simulated_data and not self._observed_data:
            dummy_observed_data_sets = len(self.simulated_data_sets)*[None]
            self.simulated_and_observed_data_sets = zip(self.simulated_data_sets, dummy_observed_data_sets)
        elif not self._simulated_data and self._observed_data:
            dummy_simulated_data_sets = len(self.observed_data_sets)*[None]
            self.simulated_and_observed_data_sets = zip(dummy_simulated_data_sets, self.observed_data_sets)
        else:
            self.simulated_and_observed_data_sets = zip(self.simulated_data_sets, self.observed_data_sets)

    def _simulated_data_only_text(self, simulated_data_set):
        text = ""
        return text

    def _observed_data_only_text(self, observed_data_set):
        text = ""
        return text

    def _simulated_and_observed_data_text(self, simulated_data_set, observed_data_set):
        text = ""
        return text

    def _begin_date(self):
        begin_date = dates.num2date(self.axs.get_xlim()[0], tz=None)  # Matplotlib adds a timezone (UTC) where all other dates being used are naive. So must remove timezone to compare with naive dates
        return begin_date

    def _end_date(self):
        end_date = dates.num2date(self.axs.get_xlim()[1], tz=None)  # Matplotlib adds a timezone (UTC) where all other dates being used are naive. So must remove timezone to compare with naive dates
        return end_date

    def text(self, beg_date, end_date):
        if self._simulated_data:
            text = self.simulated_data_header
        elif self._observed_data:
            text = self.observed_data_header
        else:
            text = self.simulated_and_observed_data_header

        self.begin_date = beg_date.replace(tzinfo=None)
        self.end_date = end_date.replace(tzinfo=None)
        self._observed_and_simulated_data()
        for simulated_data, observed_data in self.simulated_and_observed_data_sets:
            if simulated_data == None:
                text += self._observed_data_only_text(observed_data)
            elif observed_data == None:
                text += self._simulated_data_only_text(simulated_data)
            else:
                text += self._simulated_and_observed_data_text(simulated_data, observed_data)
        return text[0:-1]

    def add_anchor_text(self):
        text = self.text(self._begin_date(), self._end_date())
        self.anchor_text = AnchoredText(text, prop=dict(size="xx-small", fontfamily="Monospace"),
                                        frameon=True,
                                        loc='upper right')
        self.anchor_text.patch.set_alpha(0.2)
        self.anchor_text.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        self.axs.add_artist(self.anchor_text)

    def update_anchor_text(self, begin_date, end_date):
        text = self.text(begin_date, end_date)
        self.anchor_text.txt.set_text(text)
