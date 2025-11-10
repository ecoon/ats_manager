import os
import grp
import configparser


def get_default_config():
    """Dictionary of all config option defaults.

    Returns
    -------
    rcParams : configparser.ConfigParser
      A dict-like object containing parameters.
    """
    rcParams = configparser.ConfigParser()

    # folder structure
    rcParams['DEFAULT']['ATS_BASE'] = os.path.join(os.environ['HOME'], 'ats')
    rcParams['DEFAULT']['ATS_BUILD_BASE'] = rcParams['DEFAULT']['ATS_BASE']

    # groups and permissions
    rcParams['DEFAULT']['ATS_ADMIN_GROUP'] = ''
    return rcParams


def get_config():
    rcParams = get_default_config()

    if 'ATS_BASE' in os.environ:
        rcParams['DEFAULT']['ATS_BASE'] = os.environ['ATS_BASE']
    if 'ATS_BUILD_BASE' in os.environ:
        rcParams['DEFAULT']['ATS_BUILD_BASE'] = os.environ['ATS_BUILD_BASE']
    else:
        rcParams['DEFAULT']['ATS_BUILD_BASE'] = rcParams['DEFAULT']['ATS_BASE']

    
    # paths to search for rc files
    rc_paths = [
        os.path.join(os.environ['HOME'], 'ats_manager.cfg'),
        os.path.join(os.getcwd(), 'ats_manager', 'ats_manager.cfg'),
        os.path.join(os.getcwd(), 'ats_manager.cfg'),
    ]

    # read the rc files
    rcParams.read(rc_paths)
    return rcParams


config = get_config()['DEFAULT']
