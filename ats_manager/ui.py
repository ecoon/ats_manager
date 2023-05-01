import argparse

def get_install_args(parser, ats=False):
    groups = dict()
    # main names
    parser.add_argument('build_name', type=str,
                        help='Arbitrary name of the build.  Typically the branch name.')

    # control
    groups['control'] = parser.add_argument_group('control', 'flags for controlling the build process')
    groups['control'].add_argument('--skip-amanzi-tests', action='store_true',
                                   help='Skip running Amanzi tests.')
    if ats:
        groups['control'].add_argument('--skip-ats-tests', action='store_true',
                            help='Skip running ATS tests.')
    skip_clobber = groups['control'].add_mutually_exclusive_group()
    skip_clobber.add_argument('--skip-clone', action='store_true',
                        help='Skip cloning (and use existing repos)')
    skip_clobber.add_argument('--clobber', action='store_true',
                        help='Clobber any existing repos.')
    groups['control'].add_argument('--machine', default=None,
                                   help='Machine name to include in modulefile name')
    groups['control'].add_argument('--compiler-id', type=str, default=None,
                                   help='Identifying string for the compiler, MPI, or any other toolchain versions or identifiers that will ensure this is unique from all other builds of the same source.')
    groups['control'].add_argument('--mpi-wrapper-kind', type=str, default='mpi',
                                   choices=['mpi','intel','vendor'],
                                   help="Type of wrappers used to find the wrapper executables.  Valid include:\n  mpi = mpicc, mpicxx, mpifort\n  intel = mpiicc, mpiicpc, mpiiftn\n  vendor = cc, CC, ftn")
    
    # branches
    groups['branches'] = parser.add_argument_group('branches', 'current and new branch names')
    groups['branches'].add_argument('--repo', type=str, default=None,
                        help='Arbitrary name of the repository.  Typically the branch name.  Defaults to BUILD_NAME.')
    groups['branches'].add_argument('--amanzi-branch', type=str, default=None,
                        help='(Existing) branch or hash of Amanzi to check out.  Defaults to BUILD_NAME')
    if ats:
        groups['branches'].add_argument('--ats-branch', type=str, default=None,
                            help='(Existing) branch or hash of ATS to check out.  Defaults to the hash of the submodule in AMANZI_BRANCH.')
        
    groups['branches'].add_argument('--new-amanzi-branch', type=str, default=None,
                        help='Create a new branch of Amanzi, starting from AMANZI_BRANCH.')
    if ats:
        groups['branches'].add_argument('--new-ats-branch', type=str, default=None,
                            help='Create a new branch of ATS, starting from ATS_BRANCH.')

    # tpl control
    groups['tpls'] = parser.add_argument_group('TPLs', 'third party library controls')
    groups['tpls'].add_argument('--modulefile', type=str, action='append', default=list(),
                                help='Name of a modulefile to load, can appear multiple times.  Note this is unnecessary if the TPLs already exist.')
    groups['tpls'].add_argument('--enable-geochemistry', action='store_true',
                        help='Build with geochemistry physics package')
    if not ats:
        groups['tpls'].add_argument('--enable-structured', action='store_true',
                            help='Build with geochemistry physics package')
    groups['tpls'].add_argument('--build-static', action='store_true',
                                help='Build with static libraries')
        
    # build type
    valid_build_types = ['debug', 'opt', 'relwithdebinfo']
    groups['build_type'] = parser.add_argument_group('build_type', 'controls optimization flags')
    groups['build_type'].add_argument('--build-type', type=str, default='debug', choices=valid_build_types,
                        help='Amanzi build type')
    groups['build_type'].add_argument('--tpls-build-type', type=str, default=None, choices=valid_build_types,
                                      help='TPLs build type')
    groups['build_type'].add_argument('--trilinos-build-type', type=str, default=None, choices=valid_build_types,
                                      help='TPLs build type')

    groups['build_type'].add_argument('--bootstrap-options', type=str, default='',
                                      help='Additional options passed to bootstrap')
                                      

    return parser, groups

def get_update_args(parser, ats=False):
    parser.add_argument('modulefile', type=str,
                        help='Name of the modulefile (e.g. ats/master/debug)')
    parser.add_argument('--skip-recompile', action='store_true',
                        help='Skip re-compiling.')
    parser.add_argument('--skip-amanzi-tests', action='store_true',
                        help='Skip running Amanzi tests.')
    if ats:
        parser.add_argument('--skip-ats-tests', action='store_true',
                            help='Skip running ATS tests.')
    return
        

def get_clean_args(parser):
    parser.add_argument('module_name', type=str,
                        help='Name of the modulefile (e.g. ats/master/debug)')
    parser.add_argument('-x', '--remove', action='store_true',
                        help='Complete removal of the modulefile, repo, etc.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Removes files and directories without prompting.')
    return
