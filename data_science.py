#!/usr/bin/python3
from datetime import datetime, timedelta, timezone
from re import findall

def read_log_file(log_file_pathname):
    '''
    Task:
        Read log file and return data in file
    :param log_file_pathname: path of file
    :return string
    '''
    with open(log_file_pathname, 'r') as f:
        data = f.readlines()
    return "".join(data)


def parse_log_start_time(log_data):
    """
    Task:
        - Take first line of data then get data & time
        - Use datetime.strptime parse a human-readable date time to
        datetime.datetime
        - Get offset timezone in log file
        - Recreate datetime.datetime with timezone
    :param log_data: content of file
    :return datetime.datetime
    """
    start_time = "".join(log_data.split('\n')[0].split('at ')[1:])
    now = datetime.strptime(start_time, "%A, %B %d, %Y %H:%M:%S")
    time_zone = read_configuration(log_data)['g_timezone']
    return datetime(now.year,
                             now.month,
                             now.day,
                             now.hour,
                             now.minute,
                             now.second,
                             tzinfo=timezone(timedelta(hours=int(time_zone))))


def read_configuration(log_data):
    """
    Task:
        - Find all configuration in log file
        - Match setting with value into dic
    :return dictionary
    """
    configuration = findall(r"Lua cvar: \([a-zA-Z_+\-,.0-9/]*", log_data)
    settings = {}
    for sett in configuration:
        config, value = sett.split("(")[1].split(",")
        settings[config] = value
    return settings
