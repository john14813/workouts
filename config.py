'''
config.py
'''
# pylint:disable=broad-exception-caught

# std
from os import getenv

# venv
from loguru import logger

# read config file member
def get_config ():
    '''
    # open the config file 
    # return dict of elements
    # config_file defined in env as config_file
    '''
    config_file = getenv("config_file", "workouts.config")

    retval = {}

    lines = []
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            # Strip newline characters and ignore empty lines if needed
            lines = [line.rstrip('\n') for line in file]
    except FileNotFoundError:
        print(f"Error: File '{config_file}' not found.")
    except PermissionError:
        print(f"Error: Permission denied for file '{config_file}'.")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")

    for line in lines:
        # if empty, continue
        if len(line) == 0:
            continue

        # if starts with # continue
        if line[0] == '#':
            continue

        # parse before, after '='
        pline=line.rstrip().split('=')

        if len(pline) == 2:
            retval[pline[0]] = pline[1]

    # echo to log
    for k, v in retval.items():
        logger.info(f"{k} {v}")

    return retval
