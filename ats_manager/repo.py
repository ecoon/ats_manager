import os, shutil
import logging
import git

import ats_manager.names as names
import ats_manager.utils as utils
from ats_manager.config import config

def clone(name, url, path, branch='master'):
    """Generic clone helper"""
    if os.path.exists(path):
        raise RuntimeError("Cannot clone into {} as it already exists.".format(path))

    logging.info('Cloning {}'.format(name))
    logging.info('   from: {}'.format(url))
    logging.info('     to: {}'.format(path))
    logging.info(' branch: {}'.format(branch))
    repo = git.Repo.clone_from(url, path, branch=branch)
    utils.chmod(path)
    return repo


def clone_amanzi(path, branch='master'):
    """Clones a new copy of an Amanzi branch."""
    return clone('Amanzi', config['AMANZI_URL'], path, branch)


def clone_amanzi_ats(path, branch='master', ats_branch=None):
    """Clones a new copy of an Amanzi branch that includes ATS."""
    repo = clone('Amanzi-ATS', config['AMANZI_URL'], path, branch)
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


def create_new_branch(repo, branch):
    repo.git.checkout('-b', branch)


def get_repo(repo_kind, repo_version,
             skip_clone=False,
             clobber=False,
             amanzi_branch=None,
             ats_branch=None,
             new_amanzi_branch=None,
             new_ats_branch=None):
    """Check or clone a repo, returns the path to the repo"""
    amanzi_repo_path = names.amanzi_src_dir(repo_kind, repo_version)
    logging.info(f'Setting up repo at: {amanzi_repo_path}')
    logging.info(f'   skip_clone = {skip_clone}, clobber = {clobber}')
    
    if skip_clone:
        amanzi_repo = git.Repo(amanzi_repo_path)
    else:
        if clobber:
            logging.info(f'   clobbering dir: {amanzi_repo_path}')
            ats_clean.remove_dir(amanzi_repo_path, True)

        if amanzi_branch is None:
            amanzi_branch = repo_version

        logging.info(f'   switching to branches: {amanzi_branch}, {ats_branch}')
        amanzi_repo = clone_amanzi_ats(amanzi_repo_path, amanzi_branch, ats_branch)

    if new_amanzi_branch is not None:
        logging.info(f'   creating Amanzi branch: {new_amanzi_branch}')
        amanzi_repo.git.checkout('-b', new_amanzi_branch)
    if new_ats_branch is not None:
        logging.info(f'   creating ATS branch: {new_ats_branch}')
        amanzi_repo.submodule(names.ats_submodule).module().git.checkout('-b', new_ats_branch)

    utils.chmod(amanzi_repo_path)
    return amanzi_repo


        
