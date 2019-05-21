#!/usr/bin/python3
from datetime import datetime, timedelta, timezone
from re import findall, split
import csv
from sqlite3 import connect as connect_sqlite
from psycopg2 import Error, connect as connect_psql


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
    time_humnan_readable = "".join(log_data.split('\n')[0].split('at ')[1:])
    start_time = datetime.strptime(
        time_humnan_readable, "%A, %B %d, %Y %H:%M:%S")
    time_zone = read_configuration(log_data)['g_timezone']
    return datetime(start_time.year,
                    start_time.month,
                    start_time.day,
                    start_time.hour,
                    start_time.minute,
                    start_time.second,
                    tzinfo=timezone(timedelta(hours=int(time_zone))))


def read_configuration(log_data):
    """
    Task:
        - Find all configuration in log file
        - Match setting with value into dic
    :param log_data: content of file
    :return dictionary
    """
    configuration = findall(r"Lua cvar: \([a-zA-Z_+\-,.0-9/]*", log_data)
    settings = {}
    for sett in configuration:
        config, value = sett.split("(")[1].split(",")
        settings[config] = value
    return settings


def parse_session_mode_and_map(log_data):
    """
    Task:
        - Find map & mode
        - Match setting with value into dic
    :param log_data: content of file
    :return tuple
    """
    map_mode = findall(
        r"Loading level [a-zA-Z_+\-,.0-9/ ]*\w", log_data)[0].split("Loading level ")[1]
    s_map = map_mode.split(',')[0].split('/')[1]
    s_mode = map_mode.split(' ')[::-1][0]
    return (s_mode, s_map)


def parse_frags(log_data):
    """
    Task:
        - Find list of frags
        - frag_time (required): time when the frag occurred in the format MM:SS;
        - killer_name (required): username of the player who fragged another or killed himself;
        - victim_name (optional): username of the player who has been fragged;
        - weapon_code (optional): code name of the weapon that was used to frag.
    Example:
        <37:45> <Lua> papazark killed theprophete with P90
        <38:03> <Lua> lamonthe killed itself
    :param log_data: content of file
    :return tuple
    """
    frags = []
    time_increase = 0
    last_frag = None
    match = findall(
        r"<\d\d:\d\d> <Lua> [a-zA-Z_+\-,.0-9/ ]* killed [a-zA-Z_+\-,.0-9/ ]*\w", log_data)
    for info in match:
        frag_killer, victim_weapon = split(r" killed ", info)
        frag_time, killer_name = split(r" <Lua> ", frag_killer)
        frag_time = frag_time.strip('<>')

        if last_frag and frag_time < last_frag:
            time_increase = time_increase + 1
        last_frag = frag_time
        frag_time = handle_frag_time(parse_log_start_time(
            log_data), frag_time, time_increase)

        victim_name, weapon_code = split(
            r" with ", victim_weapon) if 'with' in victim_weapon else [None, None]
        frags.append((frag_time, killer_name) if not victim_name else (
            frag_time, killer_name, victim_name, weapon_code))
    return frags


def handle_frag_time(start_time, frag_time, time_increase=0):
    senconds_sub = start_time.minute * 60 + start_time.second
    m_frag, s_frag = frag_time.split(':')
    senconds_add = (time_increase * 60 + int(m_frag)) * 60 + int(s_frag)
    return start_time + timedelta(seconds=senconds_add - senconds_sub)


def prettify_frags(frags):

    CHARACTER_BOAT = '🚤'
    CHARACTER_AUTOMOBILE = '🚙'
    CHARACTER_VICTIM = '😦'
    CHARACTER_KILLER = '😛'
    CHARACTER_SUICIDE = '☠'
    CHARACTER_GUN = '🔫'
    CHARACTER_GRENADE = '💣'
    CHARACTER_ROCKET = '🚀'
    CHARACTER_MACHETE = '🔪'

    weapon_icon = {
        'Vehicle': CHARACTER_AUTOMOBILE,
        'Falcon': CHARACTER_GUN,
        'Shotgun': CHARACTER_GUN,
        'P90': CHARACTER_GUN,
        'MP5': CHARACTER_GUN,
        'M4': CHARACTER_GUN,
        'AG36': CHARACTER_GUN,
        'OICW': CHARACTER_GUN,
        'SniperRifle': CHARACTER_GUN,
        'M249': CHARACTER_GUN,
        'VehicleMountedAutoMG': CHARACTER_GUN,
        'VehicleMountedMG': CHARACTER_GUN,
        'HandGrenade': CHARACTER_GRENADE,
        'AG36Grenade': CHARACTER_GRENADE,
        'OICWGrenade': CHARACTER_GRENADE,
        'StickyExplosive': CHARACTER_GRENADE,
        'Rocket': CHARACTER_ROCKET,
        'VehicleMountedRocketMG': CHARACTER_ROCKET,
        'VehicleRocket': CHARACTER_ROCKET,
        'Machete': CHARACTER_MACHETE,
        'Boat': CHARACTER_BOAT
    }
    emoji_frags = []
    for data in frags:
        if len(data) > 2:
            for time, killer, victim, weapon in [data]:
                emoji_frags.append("%s %s %s %s %s %s" % (str(
                    time), CHARACTER_KILLER, killer, weapon_icon[weapon], CHARACTER_VICTIM, victim))
        else:
            for time, killer in [data]:
                emoji_frags.append("%s %s %s %s %s" % (
                    str(time), CHARACTER_VICTIM, killer, weapon_icon[weapon], CHARACTER_SUICIDE))
    return emoji_frags


def parse_game_session_start_and_end_times(log_data):
    start_time = findall(r"<(\d\d:\d\d)>.*Loading level", log_data)[0]
    end_time = findall(r"<(\d\d:\d\d)>.*Statistics", log_data)[::-1]
    if not end_time:
        end_time = findall(
            r"<(\d\d:\d\d)> ERROR: \$3#SCRIPT ERROR File: =C, Function: _ERRORMESSAGE,", log_data)[::-1][0]
    else:
        end_time = end_time[::-1][0]
    start_game = parse_log_start_time(log_data)
    time_increase = 0
    if end_time < start_time:
        time_increase = 1
    start_time = handle_frag_time(start_game, start_time)
    end_time = handle_frag_time(start_game, end_time, time_increase)
    return start_time, end_time


def write_frag_csv_file(log_file_pathname, frags):
    with open(log_file_pathname, "w+") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows(frags)


def insert_match_to_sqlite(file_pathname, start_time, end_time, game_mode, map_name, frags):
    """ 
    Task:
        - Create connection with database
        - Excute sql command insert info of match into database
        - Return last row id
    :param file_pathname: database file
    :param start_time: game start time
    :param end_time: game end time
    :param game_mode: mode of game
    :param map_name: name of map
    :param frags: information frags history
    :return: last row id or None
    """
    conn = create_connection(file_pathname)
    with conn:
        c = conn.cursor()
        sql = "INSERT INTO match(start_time, end_time, game_mode, map_name) VALUES(?,?,?,?);"
        match = (start_time, end_time, game_mode, map_name)
        c.execute(sql, match)
        lastrowid = c.lastrowid
        insert_frags_to_sqlite(conn, lastrowid, frags)
    return lastrowid


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = connect_sqlite(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def insert_frags_to_sqlite(connection, match_id, frags):
    c = connection.cursor()
    for frag in frags:
        sql_killer_victim = "INSERT INTO match_frag(match_id, frag_time, killer_name, victim_name, weapon_code) VALUES(%s,?,?,?,?);" % (
            match_id)
        sql_suicide = "INSERT INTO match_frag(match_id,frag_time, killer_name) VALUES(%s,?,?);" % (
            match_id)
        if len(frag) > 2:
            c.execute(sql_killer_victim, frag)
        else:
            c.execute(sql_suicide, frag)


def insert_match_to_postgresql(properties, start_time, end_game, game_mode, map_name, frags):
    hostname, database_name, username, password = properties
    connection = connect_psql(user=username,
                                password=password,
                                host=hostname,
                                database=database_name)
    with connection:
        cursor = connection.cursor()
        sql_match = """INSERT INTO match(start_time, end_time, game_mode, map_name) VALUES(%s,%s,%s,%s) RETURNING match_id;"""
        cursor.execute(sql_match, (start_time, end_time, game_mode, map_name))
        lastrowid = cursor.fetchone()[0]
        sql_killer_victim = "INSERT INTO match_frag(match_id, frag_time, killer_name, victim_name, weapon_code) VALUES(%s,%s,%s,%s,%s);"
        sql_suicide = """INSERT INTO match_frag(match_id,frag_time, killer_name) VALUES(%s,%s,%s);"""
        for frag in frags:
            if len(frag) > 2:
                cursor.execute(sql_killer_victim, (lastrowid, *frag))
            else:
                cursor.execute(sql_suicide, (lastrowid, *frag))
        connection.commit()
    return lastrowid


if __name__ == "__main__":
    log_data = read_log_file('./logs/log04.txt')
    log_start_time = parse_log_start_time(log_data)
    frags = parse_frags(log_data)
    game_mode, map_name = parse_session_mode_and_map(log_data)
    start_time, end_time = parse_game_session_start_and_end_times(log_data)
    properties = ('127.0.0.1', 'farcry', 'postgres', '123456')
    id = insert_match_to_postgresql(properties, start_time,
                               end_time, game_mode, map_name, frags)
    print(id)
