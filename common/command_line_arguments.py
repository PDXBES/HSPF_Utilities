import sys
import getopt


def command_line_arguments(argv):
    appsettings_file_path = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile="])
    except getopt.GetoptError:
        print('<script_name.py> -i <appsetting.json path>')  # TODO could probably have this get or take the script name calllng it
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('<script_name.py> -i <appsetting.json path>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            appsettings_file_path = arg
        else:
            print("unknown option:" + opt)
            sys.exit(1)
    return appsettings_file_path
