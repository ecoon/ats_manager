import os, shutil
import git
import logging

import ats_manager.repo as repo
import ats_manager.names as names
import ats_manager.modulefile as modulefile
import ats_manager.bootstrap as bootstrap
import ats_manager.test_runner as test_runner
import ats_manager.clean as ats_clean
import ats_manager.utils as utils

from ats_manager.ui import *


def install_ats(args):
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
    args.repo_kind = 'ats'
    if args.repo is None:
        args.repo = args.build_name
    
    logging.info('Installing ATS:')
    logging.info('=============================================================================')
    logging.info('ATS name: {}'.format(args.build_name))
    logging.info('Repo version: {}'.format(args.repo))
    logging.info('ATS branch: {}'.format(args.ats_branch))
    logging.info('Amanzi branch: {}'.format(args.amanzi_branch))
    logging.info('ATS new branch: {}'.format(args.new_ats_branch))
    logging.info('Amanzi new branch: {}'.format(args.new_amanzi_branch))
    build_name = names.name('ats', args.build_name, args.machine, args.compiler_id, args.build_type)

    # repository setup
    logging.info('-----------------------------------------------------------------------------')
    repo.get_repo(args.repo_kind,
                  args.repo,
                  skip_clone=args.skip_clone,
                  clobber=args.clobber,
                  amanzi_branch=args.amanzi_branch,
                  ats_branch=args.ats_branch,
                  new_amanzi_branch=args.new_amanzi_branch,
                  new_ats_branch=args.new_ats_branch)

    # TPL setup
    logging.info('-----------------------------------------------------------------------------')
    args.enable_structured = False
    rc, tpls_name = _check_or_install_tpls(args)
    if rc != 0: return rc, tpls_name

    # modulefile setup
    logging.info('-----------------------------------------------------------------------------')
    logging.info('Generating module file:')    
    logging.info('  Fully resolved name: {}'.format(build_name))
    template_params = modulefile.create_modulefile(build_name, args.repo, tpls_name,
                                                   args.build_type)
                                 
    # bootstrap
    logging.info('-----------------------------------------------------------------------------')
    logging.info('Calling bootstrap:')
    # bootstrap, make, install
    rc = bootstrap.bootstrap_ats(build_name, args)
    if rc != 0: return rc, build_name

    # amanzi make tests
    if not args.skip_amanzi_tests:
        logging.info('Running tests:')
        rc = test_runner.amanziUnitTests(name)

    return rc, build_name


def install_amanzi(args):
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
    args.repo_kind = 'amanzi'
    if args.repo is None:
        args.repo = args.build_name

    logging.info('Installing Amanzi:')
    logging.info('=============================================================================')
    logging.info('Amanzi name: {}'.format(args.amanzi_name))
    logging.info('Repo version: {}'.format(args.repo))
    logging.info('Amanzi branch: {}'.format(args.amanzi_branch))
    logging.info('Amanzi new branch: {}'.format(args.new_amanzi_branch))
    build_name = names.name('amanzi', args.build_name, args.machine,
                            args.compiler_id, args.build_type)

    # repository setup
    logging.info('-----------------------------------------------------------------------------')
    repo.get_repo(args.repo_kind,
                  args.repo,
                  skip_clone=args.skip_clone,
                  clobber=args.clobber,
                  amanzi_branch=args.amanzi_branch,
                  ats_branch=None,
                  new_amanzi_branch=args.new_amanzi_branch,
                  new_ats_branch=None)

    # TPL setup
    logging.info('-----------------------------------------------------------------------------')
    rc, tpls_name = _check_or_install_tpls(args)
    if rc != 0: return rc, tpls_name

    # modulefile setup
    logging.info('-----------------------------------------------------------------------------')
    logging.info('Generating module file:')    
    logging.info('  Fully resolved name: {}'.format(build_name))
    template_params = modulefile.create_modulefile(build_name, args.repo, tpls_name,
                                                   args.build_type)

    # bootstrap
    logging.info('-----------------------------------------------------------------------------')
    logging.info('Calling bootstrap:')
    # bootstrap, make, install
    rc = bootstrap.bootstrap_amanzi(build_name, args)
    if rc != 0: return rc, build_name

    # amanzi make tests
    if not args.skip_amanzi_tests:
        logging.info('Running tests:')
        rc = test_runner.amanziUnitTests(name)

    return rc, build_name


def install_tpls(args):
    """Check for and create a new TPLs installation."""
    logging.info('Installing TPLs:')
    logging.info('=============================================================================')
    logging.info('TPLs version: {}'.format(args.tpls_version))
    logging.info('Repo version: {}/{}'.format(args.repo_kind, args.repo))

    assert(args.tpls_build_type is not None)
    if args.trilinos_build_type is None:
        args.trilinos_build_type = args.tpls_build_type
    
    tpls_name = names.name('amanzi-tpls', args.tpls_version,
                           args.machine, args.compiler_id, args.trilinos_build_type)

    # make the modulefile
    logging.info('-----------------------------------------------------------------------------')
    logging.info('Generating module file:')    
    logging.info(f'  Fully resolved name: {tpls_name}')
    modulefile.create_tpls_modulefile(tpls_name, args.repo_kind, args.repo,
                                      tpls_build_type=args.tpls_build_type,
                                      trilinos_build_type=args.trilinos_build_type,
                                      modulefiles=args.modulefiles)

    # bootstrap
    logging.info('-----------------------------------------------------------------------------')
    logging.info('Calling bootstrap:')
    rc = bootstrap.bootstrap_tpls(tpls_name, args)
    return rc, tpls_name


def _check_or_install_tpls(args):
    tpls_version = names.tpls_version(args.repo_kind, args.repo)
    if args.tpls_build_type is None:
        args.tpls_build_type = args.build_type

    tpls_name = names.name('amanzi-tpls', tpls_version,
                           args.machine, args.compiler_id, args.tpls_build_type)
    tpls_install_dir = names.install_dir(tpls_name)
    tpls_config_file = os.path.join(tpls_install_dir, 'share', 'cmake', 'amanzi-tpl-config.cmake')
    logging.info(f'Checking for TPLs at: {tpls_config_file}')

    if os.path.isfile(tpls_config_file):
        logging.info('  FOUND... using existing TPLs')
        return 0, tpls_name
    else:
        args.tpls_version = tpls_version
        if not hasattr(args, 'tpls_build_type'):
            args.tpls_build_type = None
        return install_tpls(args)
    

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
    
    
          
