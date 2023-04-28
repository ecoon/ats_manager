import os, shutil
import logging
import git

import ats_manager.names as names

def clone(name, url, path, branch='master'):
    """Generic clone helper"""
    if os.path.exists(path):
        raise RuntimeError("Cannot clone into {} as it already exists.".format(path))

    logging.info('Cloning {}'.format(name))
    logging.info('   from: {}'.format(url))
    logging.info('     to: {}'.format(path))
    logging.info(' branch: {}'.format(branch))
    return git.Repo.clone_from(url, path, branch=branch)


def clone_amanzi(path, branch='master'):
    """Clones a new copy of an Amanzi branch."""
    return clone('Amanzi', names.amanzi_url, path, branch)

def clone_amanzi_ats(path, branch='master', ats_branch=None):
    """Clones a new copy of an Amanzi branch that includes ATS."""
    repo = clone('Amanzi-ATS', names.amanzi_url, path, branch)
    logging.info('Cloning submodules (ATS).')

    ats_sub = repo.submodule(names.ats_submodule)
    ats_sub.update(init=True, recursive=False)

    if ats_branch is not None:
        logging.info('Checking out ATS branch: {}'.format(ats_branch))
        ats_sub.module().git.checkout(ats_branch)
        ats_sub.module().git.pull()

    # clone ats submodules
    for sub in ats_sub.module().submodules:
        logging.info('Checking out ATS submodule {}'.format(sub))
        sub.update(init=True)
    return repo

def new_branch(repo, branch):
    repo.git.checkout('-b', branch)
    



        
