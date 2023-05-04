import os,stat,sys
import subprocess
import logging

import ats_manager.names as names
from ats_manager.config import config

def script_name(prefix, name):
    return names.clean(prefix+'-'+name+'.sh')


def run_cmd(prefix, name, cmd):
    script = script_name(prefix, name)
    outfile = os.path.join(os.environ['ATS_BASE'], 'scripts', script)
    with open(outfile,'w') as fid:
        fid.write(cmd)
    os.chmod(outfile, stat.S_IRWXU) # owner r/w/x
    chmod(outfile) # group, other according to config
    return run_script(prefix, name)


def run_script(prefix, name):
    script = script_name(prefix, name)
    outfile = os.path.join(os.environ['ATS_BASE'], 'scripts', script)
    logging.info('Running {}'.format(script))
    logging.info('  file  {}'.format(outfile))
    assert(os.path.isfile(outfile))
    process = subprocess.Popen([outfile,], shell=False, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.decode('utf-8').strip())

    if process.stderr is not None:
        logging.error(process.stderr.decode('utf-8'))
    return process.returncode


def chmod(path, group=''):
    logging.info(f'  running chgrp/chmod on {path}')
    if group != '':
        group = config['ATS_ADMIN_GROUP']
    
    if group != '':
        ex = 0o775
        non_ex = 0o664
    else:
        ex = 0o755
        non_ex = 0o644

    for root, dirs, files in os.walk(path):
        for d in dirs:
            dirname = os.path.join(root, d)
            os.chmod(dirname, ex)
            if group != '':
                shutil.chown(dirname, group=group)

        for f in files:
            if not f.startswith('.#'): # dead files, go away
                filename = os.path.join(root, f)
                if os.stat(filename).st_mode & 0o00100: # is owner-executable?
                    os.chmod(filename, ex)
                else:
                    os.chmod(filename, non_ex)
                if group != '':
                    shutil.chown(filename, group=group)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    Stolen from: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
