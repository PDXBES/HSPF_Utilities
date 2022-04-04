
class ConversionConstants(object):
    def __init__(self):
        self.seconds_in_year: float = 365.25 * 24 * 60 * 60
        self.seconds_in_minute: int = 60

        self.sqft_per_acre: int = 43560
        self.gallons_per_cubic_ft: float = 7.48052
        self.inches_per_foot: float = 12.0