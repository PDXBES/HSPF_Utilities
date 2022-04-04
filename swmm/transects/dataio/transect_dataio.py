import pandas as pd


class TransectDataIo(object):
    def __init__(self):
        self.old_new_name_df = None
        self.trapezoidal_data_df = None
        self.street_transect_df = None
        self.trapezoidal_transect_df = None
        self.natural_channel_transect_df = None
        self.natural_channel_xs_transect_df = None
        self.surveyed_ditch_transect_df = None
        self.surveyed_ditch_xs_transect_df = None
        self.file_path = None

    def get_old_new_name(self, old_new_name_file_path):
        self.old_new_name_df = pd.read_csv(old_new_name_file_path)

    def get_old_new_name_data(self):
        old_names = list(self.old_new_name_df['OldName'].values)
        new_names = list(self.old_new_name_df['NewName'].values)
        old_new_name_data = dict(zip(old_names, new_names))
        return old_new_name_data

    def get_trapezoidal_transect_data(self, trapezoid_file_path):
        self.trapezoidal_data_df = pd.read_csv(trapezoid_file_path)

    def get_trapezoidal_data(self):
        trapezoidal_data = self.trapezoidal_data_df.itertuples()
        return trapezoidal_data

    def get_street_transect_data_dataframe(self):
        self.street_transect_df = pd.read_excel(self.file_path, sheet_name='Street')
        return self.street_transect_df

    def get_trapezoidal_transect_data_dataframe(self):
        self.trapezoidal_transect_df = pd.read_excel(self.file_path, sheet_name="Trapezoid")
        return self.trapezoidal_transect_df

    def get_surveyed_ditch_transect_data_dataframe(self):
        self.surveyed_ditch_transect_df = pd.read_excel(self.file_path, sheet_name='SurveyedDitch')
        return self.surveyed_ditch_transect_df

    def get_surveyed_ditch_xs_transect_data_dataframe(self):
        self.surveyed_ditch_xs_transect_df = pd.read_excel(self.file_path, sheet_name='SurveyedDitchXS')
        return self.surveyed_ditch_xs_transect_df

    def get_natural_channel_transect_data_dataframe(self):
        self.natural_channel_transect_df = pd.read_excel(self.file_path, sheet_name='NaturalChannel')
        return self.natural_channel_transect_df

    def get_natural_channel_xs_transect_data_dataframe(self):
        self.natural_channel_xs_transect_df = pd.read_excel(self.file_path, sheet_name='NaturalChannelXS')
        return self.natural_channel_xs_transect_df
