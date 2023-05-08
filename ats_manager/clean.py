"""Helper functions for cleaning builds."""

import os, shutil
import ats_manager.utils
import ats_manager.config
import logging

def _check(file_or_dirname, force):
    if not os.path.exists(file_or_dirname):
        logging.info("Not removing nonexistent directory/file: {}".format(file_or_dirname))
        return 1
    
    ats_base = ats_manager.config.config['ATS_BASE']
    ats_bbase = ats_manager.config.config['ATS_BUILD_BASE']

    if not (file_or_dirname.startswith(ats_base) or file_or_dirname.startswith(ats_bbase)):
        # make sure file_or_dirname is in that directory
        logging.warning("Directory/file '{}' not in ATS_BASE='{}' or ATS_BUILD_BASE='{}'".format(file_or_dirname, ats_base, ats_bbase))
        return 1

    # make sure it has some extra info...
    if file_or_dirname == ats_base or file_or_dirname == ats_bbase:
        logging.warning("Not removing ATS_BASE or ATS_BUILD_BASE globally")
        return 1

    # make sure it doesn't escape back up the tree
    if '..' in file_or_dirname:
        logging.warning("Directory/file '{}' contains '..' which may go somewhere bad... cowardly refusing to remove.".format(file_or_dirname))
        return 1

    # confirm with user
    if not force:
        do_it = ats_manager.utils.query_yes_no('Really remove "{}"?'.format(file_or_dirname))
        if not do_it:
            return 1

    return 0
        
def remove_file(filename, force=False):
    res = _check(filename, force)
    if res == 0:
        logging.info('Removing: {}'.format(filename))
        os.remove(filename)
    return res

def remove_dir(dirname, force=False):
    """Safely removes a directory"""
    res = _check(dirname, force)
    if res == 0:
        logging.info('Removing: {}'.format(dirname))
        shutil.rmtree(dirname, True)
    return 0
    
        
