import os, shutil
import git
import logging

import ats_manager.repo as repo
import ats_manager.names as names
import ats_manager.modulefile as modulefile
import ats_manager.bootstrap as bootstrap
import ats_manager.test_runner as test_runner
import ats_manager.clean as ats_clean

from ats_manager.ui import *

def install_ats(build_name,
                amanzi_branch=None, ats_branch=None,
                new_amanzi_branch=None, new_ats_branch=None,
                repo_version=None,
                build_type='debug',
                tpls_build_type='debug',
                machine=None,
                compiler_id=None,
                mpi_wrapper_kind=None,
                modulefiles=None,
                skip_amanzi_tests=False,
                skip_ats_tests=False,
                skip_clone=False,
                clobber=False,
                **kwargs):
    """Create a new ATS installation.

    Creates a modulefile, clones the repos, bootstraps the code, and
    runs the tests.

    To see arguments, run: `python bin/install_ats.py -h`

    Returns
    -------
    int : return code: 
        0 = success
       -1 = failed build
       >0 = successful build but failing tests
    str : name of the generated modulefile

    """
    logging.info('Installing ATS:')
    logging.info('=============================================================================')
    logging.info('ATS name: {}'.format(ats_name))
    logging.info('ATS branch: {}'.format(ats_branch))
    logging.info('Amanzi branch: {}'.format(amanzi_branch))
    logging.info('ATS new branch: {}'.format(new_ats_branch))
    logging.info('Amanzi new branch: {}'.format(new_amanzi_branch))
    logging.info('Repo version: {}'.format(repo_version))

    # argument processing
    if modulefiles is None:
        modulefiles = []
    if compiler_id is None:
        compiler_id = 'default'
    if machine is None:
        machine = 'local'
    name_args = [machine, compiler_id, build_type]
    
    # repository setup
    logging.info('-----------------------------------------------------------------------------')
    amanzi_repo = names.amanzi_src_dir('ats', repo_version)
    logging.info(f'Setting up repo at: {amanzi_repo}')
    logging.info(f'   clone = {skip_cone}, clobber = {clobber}')
    
    if skip_clone:
        amanzi_repo = git.Repo(amanzi_repo)
    else:
        if clobber:
            logging.info(f'   clobbering dir: {amanzi_repo}')
            ats_clean.remove_dir(amanzi_repo, True)
        logging.info(f'   switching to branches: {amanzi_branch}, {ats_branch}')
        amanzi_repo = repo.clone_amanzi_ats(amanzi_repo, amanzi_branch, ats_branch)

    if new_amanzi_branch is not None:
        logging.info(f'   creating Amanzi branch: {new_amanzi_branch}')
        amanzi_repo.git.checkout('-b', new_amanzi_branch)
    if new_ats_branch is not None:
        logging.info(f'   creating ATS branch: {new_ats_branch}')
        amanzi_repo.submodule(names.ats_submodule).module().git.checkout('-b', new_ats_branch)

    # TPL setup
    logging.info('-----------------------------------------------------------------------------')
    tpls_version = names.tpls_version('ats', repo_version)
    tpls_name = names.name('amanzi-tpls', tpls_version, machine, compiler_id, tpls_build_type)
    logging.info(f'Checking for TPLs at: {tpls_name}')

    rc, tpls_name = install_tpls(tpls_version,
                             'ats',
                             repo_version,
                             tpls_build_type,
                             machine,
                             compiler_id,
                             mpi_wrapper_kind,
                             modulefiles)
    if rc < 0:
        return rc, tpls_name

    # modulefile setup
    build_name = names.name('ats', build_name, *name_args)

    logging.info('-----------------------------------------------------------------------------')
    logging.info('Generating module file:')    
    logging.info('  Fully resolved name: {}'.format(build_name))

    template_params = modulefile.create_modulefile(build_name, repo_version, tpls_name,
                                 build_type=build_type)
                                 
    # bootstrap
    logging.info('Calling bootstrap:')
    # bootstrap, make, install
    rc = bootstrap.bootstrap_ats(build_name, **kwargs)
    if rc != 0:
        return -1, build_name

    # amanzi make tests
    if skip_amanzi_tests:
        amanzi_unittests_rc = 0
    else:
        logging.info('Running tests:')
        amanzi_unittests_rc = test_runner.amanziUnitTests(name)
        if amanzi_unittests_rc != 0:
            rc += 1
    return rc, name


def install_amanzi(build_name,
                   amanzi_branch=None,
                   new_amanzi_branch=None,
                   repo_version=Noen,
                   build_type='debug',
                   tpls_build_type='debug',
                   machine=None,
                   compiler_id=None,
                   mpi_wrapper_kind=None,
                   modulefiles=None,
                   skip_amanzi_tests=False,
                   skip_clone=False,
                   clobber=False,
                   **kwargs):
    """Create a new Amanzi installation.

    Creates a modulefile, clones the repos, bootstraps the code, and
    runs the tests.

    To see arguments, run: `python bin/install_amanzi.py -h`

    Returns
    -------
    int : return code: 
        0 = success
       -1 = failed build
       >0 = successful build but failing tests
    str : name of the generated modulefile

    """
    logging.info('Installing Amanzi:')
    logging.info('=============================================================================')
    logging.info('Amanzi name: {}'.format(amanzi_name))
    logging.info('Amanzi branch: {}'.format(amanzi_branch))
    logging.info('Amanzi new branch: {}'.format(new_amanzi_branch))
    logging.info('Repo version: {}'.format(repo_version))

    # argument processing
    if modulefiles is None:
        modulefiles = []
    if compiler_id is None:
        compiler_id = 'default'
    if machine is None:
        machine = 'local'
    name_args = [machine, compiler_id, build_type]

    # repository setup
    logging.info('-----------------------------------------------------------------------------')
    amanzi_repo = names.amanzi_src_dir('amanzi', repo_version)
    logging.info(f'Setting up repo at: {amanzi_repo}')
    logging.info(f'   clone = {skip_cone}, clobber = {clobber}')
    
    if skip_clone:
        amanzi_repo = git.Repo(amanzi_repo)
    else:
        if clobber:
            logging.info(f'   clobbering dir: {amanzi_repo}')
            ats_clean.remove_dir(amanzi_repo, True)
        logging.info(f'   switching to branches: {amanzi_branch}')
        amanzi_repo = repo.clone_amanzi(amanzi_repo, amanzi_branch)

    if new_amanzi_branch is not None:
        logging.info(f'   creating Amanzi branch: {new_amanzi_branch}')
        amanzi_repo.git.checkout('-b', new_amanzi_branch)

    # TPL setup
    logging.info('-----------------------------------------------------------------------------')
    tpls_version = names.tpls_version('amanzi', repo_version)
    tpls_name = names.name('amanzi-tpls', tpls_version, machine, compiler_id, tpls_build_type)
    logging.info(f'Checking for TPLs at: {tpls_name}')

    rc, tpls_name = install_tpls(tpls_version,
                             'amanzi',
                             repo_version,
                             tpls_build_type,
                             machine,
                             compiler_id,
                             mpi_wrapper_kind,
                             modulefiles)
    if rc < 0:
        return rc, tpls_name


    # modulefile setup
    build_name = names.name('amanzi', build_name, *name_args)

    logging.info('-----------------------------------------------------------------------------')
    logging.info('Generating module file:')    
    logging.info('  Fully resolved name: {}'.format(build_name))

    template_params = modulefile.create_modulefile(build_name, repo_version, tpls_name,
                                 build_type=build_type)
                                 
    # bootstrap
    logging.info('Calling bootstrap:')
    # bootstrap, make, install
    rc = bootstrap.bootstrap_amanzi(build_name, **kwargs)
    if rc != 0:
        return -1, build_name

    # amanzi make tests
    if skip_amanzi_tests:
        amanzi_unittests_rc = 0
    else:
        logging.info('Running tests:')
        amanzi_unittests_rc = test_runner.amanziUnitTests(name)
        if amanzi_unittests_rc != 0:
            rc += 1
    return rc, name



def clean(module_name, remove=False, force=False):
    """Cleans or completely removes a build.

    By defualt, this removes: 
     * AMANZI_BUILD_DIR
     * AMANZI_DIR
     * AMANZI_TPLS_BUILD_DIR
     * AMANZI_TPLS_DIR

    If remove == True, this also removes:
     * AMANZI_SRC_DIR
     * modulefile
     * all bootstrap scripts
     * any test directories

    """
    amanzi_install_dir = names.amanzi_install_dir(module_name)
    ats_clean.remove_dir(amanzi_install_dir, force)

    amanzi_build_dir = names.amanzi_build_dir(module_name)
    ats_clean.remove_dir(amanzi_build_dir, force)

    tpls_install_dir = names.tpls_install_dir(module_name)
    ats_clean.remove_dir(tpls_install_dir, force)

    tpls_build_dir = names.tpls_build_dir(module_name)
    ats_clean.remove_dir(tpls_build_dir, force)

    if remove:
        amanzi_src_dir = names.amanzi_src_dir(module_name)
        ats_clean.remove_dir(amanzi_src_dir, force)

        bootstrap_script = utils.script_name('bootstrap', module_name)
        if os.path.exists(bootstrap_script):
            os.remove(bootstrap_script)

        modulefile = names.modulefile_path(module_name)
        if os.path.exists(modulefile):
            os.remove(modulefile)

    return 0, module_name
    
    
          
