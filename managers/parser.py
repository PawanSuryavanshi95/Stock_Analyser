class Parser:

    def __init__(self):
        pass

    def parse_alpha_vantage_response(self, res):
        time_series_data = None

        for key in list(res.keys()):
            if "Time Series" in key:
                time_series_data = res[key]

        return time_series_data

    def parse_twelve_data_response(self, res):
        
        return res['values']