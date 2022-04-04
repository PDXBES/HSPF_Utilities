# Print iterations progress
from datetime import datetime


class SimpleProgressBar(object):
    def __init__(self):
        self.start_time = datetime.now()

    def reading_input_data(self, iteration, total,suffix=''):
        prefix = 'Reading Input Data'
        self.print_progressbar(iteration, total, prefix, suffix)

    def finished_reading_input_data(self, iteration, total):
        prefix = 'Finished Reading Input Data'
        self.print_progressbar(iteration, total, prefix)

    def writing_geojson(self, iteration, total, suffix=''):
        prefix = 'Writing Geojson'
        self.print_progressbar(iteration, total, prefix, suffix)

    def finished_writing_geojson(self, iteration, total):
        prefix = 'Finished Writing Geojson'
        self.print_progressbar(iteration, total, prefix)

    def writing_to_gdb(self, iteration, total, suffix=''):
        prefix = 'Writing to gdb'
        self.print_progressbar(iteration, total, prefix, suffix)

    def finished_writing_to_gdb(self, iteration, total):
        prefix = 'Finished Writing to gdb'
        self.print_progressbar(iteration, total, prefix)

    def print_progressbar(self, iteration, total, prefix='',
                           suffix='', decimals=1, length=15, fill='█', print_end="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:<." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('{:>35s} |{:15s}| {:4s}% {:<25s}'.format(prefix, bar, percent, suffix), end=print_end)
        # Print New Line on Complete
        if iteration == total:
            print()

    def finish(self):
        end_time = datetime.now()
        total_seconds = round((end_time - self.start_time).total_seconds(), 0)
        seconds = int(total_seconds % 60)
        minutes = int((total_seconds - seconds)/60 % 60)
        hours = int((total_seconds - seconds - minutes*60)/3600)
        print("    Run Time: {:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
