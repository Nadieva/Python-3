import re
import argparse
import csv
from datetime import datetime
import os


def main():
    args = check_arguments()
    data_file = "data.csv"
    v_delimiter = ","
    v_action = args.action
    v_device_id = args.device_id
    v_measurement_name = args.measurement_name
    v_start_timestamp = args.start_timestamp
    v_end_timestamp = args.end_timestamp

    # Raw print arguments
    print("INFOS:")
    print("action: ", v_action)
    print("device id :", v_device_id)
    print("measurement name:", v_measurement_name)
    print("start_timestamp :", v_start_timestamp)
    print("end timestamp:", v_end_timestamp)
    print("-----------------------------------------------------------------------------------------------------------")
    if data_file is not None and os.stat(data_file).st_size != 0:
        list = measurement_list(data_file, v_measurement_name, v_device_id, v_start_timestamp, v_end_timestamp, v_delimiter)
        if v_action[0] == "min":
            print(" Min : {}" .format(min(list)))
        elif v_action[0] == "max":
            print(" Max : {}" .format(max(list)))
        elif v_action[0] == "cnt":
            print(" Total count : {}" .format(len(list)))
        elif v_action[0] == "avg":
            if len(list) > 0:
                print(" Average : {}".format(sum(list) / len(list)))
            else:
                print(" Average : 0")


#check entered arguments
def check_arguments():
    from datetime import datetime
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory and optional arguments
    parser.add_argument('action', nargs=1, help="action to do (please write in lower case)", choices=["min", "max", "avg", "cnt"], type=str)
    parser.add_argument('device_id', nargs='?', help='device ID with format according to RFC4122', type=lambda s: valid_uuid(s), default=None)
    parser.add_argument('measurement_name', nargs='?', help='measurement type', type=lambda n: valid_measurement_name(n), default=None)
    parser.add_argument('start_timestamp', nargs='?', help="Format YYYY-MM-DD HH:MM:SS.msec", type=lambda s: valid_date(s), default=None)
    parser.add_argument('end_timestamp', nargs='?', help="Format YYYY-MM-DD HH:MM:SS.msec", type=lambda s: valid_date(s), default=datetime.now())
    args = parser.parse_args()
    return args


#list of requested measurement values
def measurement_list(data_file, v_measurement_name, v_device_id, v_start_timestamp, v_end_timestamp, v_delimiter):
    #check dates
    if v_start_timestamp is None:
        v_start_timestamp = datetime.strptime('1970-01-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    elif v_start_timestamp <= v_end_timestamp:
        pass
    else:
        temp = v_start_timestamp
        v_start_timestamp = v_end_timestamp
        v_end_timestamp = temp

    #list
    values = []
    f = open(data_file, 'r')
    with f:
        reader = csv.reader(f, delimiter=v_delimiter)
        for line in reader:
            if v_device_id is not None and v_measurement_name is not None and v_device_id == line[0] and v_measurement_name == line[2] and v_start_timestamp <= datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f') <= v_end_timestamp:
                values.append(float(line[3]))
            elif v_device_id is not None and v_measurement_name is None and v_device_id == line[0] and v_start_timestamp <= datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f') <= v_end_timestamp:
                values.append(float(line[3]))
            elif v_device_id is None and v_measurement_name is not None and v_measurement_name == line[2] and v_start_timestamp <= datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f') <= v_end_timestamp:
                values.append(float(line[3]))
            elif v_device_id is None and v_measurement_name is None and v_start_timestamp <= datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f') <= v_end_timestamp:
                values.append(float(line[3]))
    return values


#check date format YYYY-MM-DD HH:MM:SS.msec
def valid_date(s):
    from datetime import datetime
    try:
        regex = re.compile('[0-9]{4}\-[0-9]{2}\-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}', re.I)
        m = regex.match(str(s))
        if bool(m):
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


#check UUID format according to the RFC4122 rule
def valid_uuid(u):
    try:
        regex = re.compile('[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}', re.I)
        m = regex.match(str(u))
        if bool(m):
            return str(u)
    except ValueError:
        return None


#check  mesurement name format
def valid_measurement_name(name):
    if not name[0].isdigit() and all(c.isalnum() or c == '_' for c in name):
        return str(name)


if __name__ == '__main__':
    main()

