from plotting.businessclasses.anchor_text_data import AnchorTextData


class AnchorTextPeakAndTotalPrecip(AnchorTextData):
    def __init__(self, axs, observed_data=None):
        super(AnchorTextPeakAndTotalPrecip, self).__init__(axs, observed_data, None)
        self.observed_data_text_format = '{1:>3} {2:^9.{0}f} {3:^8.{0}f}\n'
        self.observed_data_header = '{0:>3s} {1:9s} {2:8s}\n'.format('RG', 'Peak [in]', 'Tot [in]')
        self.precision = 2

    def _observed_data_only_text(self, observed_data):
        text = ""
        observed_peak_precip = observed_data.peak_precipitation(self.begin_date, self.end_date)
        observed_total_precip = observed_data.total_precipitation(self.begin_date, self.end_date)
        text += self.observed_data_text_format.format(self.precision, observed_data.h2_number, observed_peak_precip,
                                                      observed_total_precip)
        return text

