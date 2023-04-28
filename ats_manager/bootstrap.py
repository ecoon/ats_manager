"""Sets up and runs bootstrap"""
import os,sys,stat,shutil
import subprocess
import logging
import ats_manager.names as names
import ats_manager.utils as utils

def bootstrapExistingFromFile(module_name):
    logging.info('Bootstrap for: {}'.format(module_name))
    logging.info('Bootstrap: {}'.format(utils.script_name('bootstrap', module_name)))
    return utils.run_script('bootstrap', module_name)


def _set_arg(args, key, val):
    if val:
        args[key] = 'enable'
    else:
        args[key] = 'disable'
        

_compiler_tmp = "--with-c-compiler={cc} --with-cxx-compiler={cxx} --with-fort-compiler={ftn}"
def get_compilers(cc, cxx, ftn):
    return _compiler_tmp.format(cc, cxx, ftn)

def _which(cc, cxx, ftn):
    if cc is not None:
        cc = shutil.which(cc)
    if cxx is not None:
        cxx = shutil.which(cxx)
    if ftn is not None:
        ftn = shutil.which(ftn)
    return cc, cxx, ftn

def which_compilers(family=None, cc=None, cxx=None, ftn=None):
    cc1 = None,
    cxx1 = None
    ftn1 = None
    
    if family == 'mpi':
        cc1 = 'mpicc'
        cxx1 = 'mpicxx'
        ftn1 = 'mpifort'
    elif family == 'vendor':
        cc1 = 'cc'
        cxx1 = 'CC'
        ftn1 = 'ftn'
    elif family is None:
        pass
    else:
        raise ValueError(f'Unknown compiler family {family}')

    if cc is not None: cc1 = cc
    if cxx is not None: cxx1 = cxx
    if ftn is not None: ftn1 = ftn
    return _which(cc, cxx, ftn)


_bootstrap_tpls_template = \
"""#!/usr/bin/env bash

if [ -z "${{MODULESHOME}}" ]; then
    source ${{MODULESHOME}}/init/profile;
fi
module load {module_name}

cd ${{AMANZI_SRC_DIR}}

echo "Building Amanzi TPLs: {module_name}"
echo "-----------------------------------------------------"
echo "AMANZI_SRC_DIR = ${{AMANZI_SRC_DIR}}"
echo "AMANZI_BUILD_DIR= ${{AMANZI_BUILD_DIR}}"
echo "AMANZI_DIR = ${{AMANZI_DIR}}"
echo ""
echo "AMANZI_TPLS_BUILD_DIR = ${{AMANZI_TPLS_BUILD_DIR}}"
echo "AMANZI_TPLS_DIR = ${{AMANZI_TPLS_DIR}}"
echo "-----------------------------------------------------"

./bootstrap.sh \
    --disable-build_amanzi \
    --${{AMANZI_TRILINOS_BUILD_TYPE}}_trilinos \
    --${{AMANZI_TPLS_BUILD_TYPE}}_tpls \
    --parallel=8 \
    {shared_libs} \
    {compilers} \
    {flags} \
    --tpl-build-dir=${{AMANZI_TPLS_BUILD_DIR}} \
    --tpl-install-prefix=${{AMANZI_TPLS_DIR}} \
    --tpl-download-dir=${{ATS_BASE}}/amanzi-tpls/Downloads \
    --{structured}-structured \
    --{geochemistry}-geochemistry \
    --{geochemistry}-petsc \
    --{geochemistry}-alquimia \
    --{geochemistry}-pflotran \
    --{geochemistry}-crunchtope \
    --enable-hypre \
    --enable-silo \
    --enable-clm \
    --with-python={python_interp}

exit $?
""" 
def bootstrap_tpls(module_name,
                   compilers='mpi',
                   enable_structured=False,
                   enable_geochemistry=True,
                   bootstrap_options=None,
                   build_static=False):
    args = dict()
    args['module_name'] = module_name
    args['python_interp'] = sys.executable

    if build_static:
        args['shared_libs'] = '--disable-shared'
    else:
        args['shared_libs'] = '--enable-shared'

    _set_arg(args, 'structured', enable_structured)
    _set_arg(args, 'geochemistry', enable_geochemistry)

    args['compilers'] = get_compilers(*which_compilers(compilers))
    if bootstrap_options is None:
        args['flags'] = ''
    else:
        args['flags'] = bootstrap_options

    logging.info('Filling bootstrap')
    logging.info(args)
    cmd = _bootstrap_tpls_template.format(**args)
    logging.info(cmd)
    return utils.run_cmd('bootstrap', module_name, cmd)


_bootstrap_amanzi_template = \
"""#!/usr/bin/env bash

if [ -z "${{MODULESHOME}}" ]; then
    source ${{MODULESHOME}}/init/profile;
fi
module load {module_name}

cd ${{AMANZI_SRC_DIR}}

echo "Building Amanzi: {module_name}"
echo "-----------------------------------------------------"
echo "AMANZI_SRC_DIR = ${{AMANZI_SRC_DIR}}"
echo "AMANZI_BUILD_DIR= ${{AMANZI_BUILD_DIR}}"
echo "AMANZI_DIR = ${{AMANZI_DIR}}"
echo ""
echo "AMANZI_TPLS_BUILD_DIR = ${{AMANZI_TPLS_BUILD_DIR}}"
echo "AMANZI_TPLS_DIR = ${{AMANZI_TPLS_DIR}}"
echo "-----------------------------------------------------"

./bootstrap.sh \
    --${{AMANZI_BUILD_TYPE}} \
    {shared_libs} \
    --parallel=8 \
    --amanzi-build-dir=${{AMANZI_BUILD_DIR}} \
    --amanzi-install-prefix=${{AMANZI_DIR}} \
    --{structured}-structured \
    --{geochemistry}-geochemistry \
    --{geochemistry}-petsc \
    --{geochemistry}-alquimia \
    --{geochemistry}-pflotran \
    --{geochemistry}-crunchtope \
    --enable-amanzi_physics \
    --enable-hypre \
    --disable-silo \
    --disable-clm \
    --disable-ats_physics \
    --with-python={python_interp} \
    {flags} \
    --tpl-config-file=${{AMANZI_TPLS_CONFIG}}

exit $?
""" 
def bootstrap_amanzi(module_name,
                     compilers='mpi',
                     enable_structured=False,
                     enable_geochemistry=True,
                     bootstrap_options=None,
                     build_static=False):
    
    args = dict()
    args['module_name'] = module_name
    args['python_interp'] = sys.executable

    if build_static:
        args['shared_libs'] = '--disable-shared'
    else:
        args['shared_libs'] = '--enable-shared'

    _set_arg(args, 'structured', enable_structured)
    _set_arg(args, 'geochemistry', enable_geochemistry)

    if bootstrap_options is None:
        args['flags'] = ''
    else:
        args['flags'] = bootstrap_options

    logging.info('Filling bootstrap')
    logging.info(args)
    cmd = _bootstrap_amanzi_template.format(**args)
    logging.info(cmd)
    
    return utils.run_cmd('bootstrap', module_name, cmd)
        

_bootstrap_ats_template = \
"""#!/usr/bin/env bash

if [ -z "${{MODULESHOME}}" ]; then
    source ${{MODULESHOME}}/init/profile;
fi
module load {module_name}

cd ${{AMANZI_SRC_DIR}}

echo "Building Amanzi-ATS: {module_name}"
echo "-----------------------------------------------------"
echo "AMANZI_SRC_DIR = ${{AMANZI_SRC_DIR}}"
echo "AMANZI_BUILD_DIR= ${{AMANZI_BUILD_DIR}}"
echo "AMANZI_DIR = ${{AMANZI_DIR}}"
echo ""
echo "AMANZI_TPLS_BUILD_DIR = ${{AMANZI_TPLS_BUILD_DIR}}"
echo "AMANZI_TPLS_DIR = ${{AMANZI_TPLS_DIR}}"
echo "-----------------------------------------------------"

./bootstrap.sh \
    --${{AMANZI_BUILD_TYPE}} \
    {shared_libs} \
    --parallel=8 \
    --amanzi-build-dir=${{AMANZI_BUILD_DIR}} \
    --amanzi-install-prefix=${{AMANZI_DIR}} \
    --disable-structured \
    --{geochemistry}-geochemistry \
    --{geochemistry}-petsc \
    --{geochemistry}-alquimia \
    --{geochemistry}-pflotran \
    --{geochemistry}-crunchtope \
    --disable-amanzi_physics \
    --enable-ats_physics \
    --enable-hypre \
    --enable-silo \
    --enable-clm \
    --enable-reg_tests \
    --with-python={python_interp} \
    --ats_dev \
    {flags} \
    --tpl-config-file=${{AMANZI_TPLS_CONFIG}}

exit $?
""" 
def bootstrap_ats(module_name,
                  enable_geochemistry=False,
                  bootstrap_options=None,
                  build_static=False):
    args = dict()
    args['module_name'] = module_name
    args['python_interp'] = sys.executable

    if build_static:
        args['shared_libs'] = '--disable-shared'
    else:
        args['shared_libs'] = '--enable-shared'
        
    _set_arg(args, 'geochemistry', enable_geochemistry)

    if bootstrap_options is None:
        args['flags'] = ''
    else:
        args['flags'] = bootstrap_options

        
    logging.info('Filling bootstrap command:')
    logging.info(args)
    cmd = _bootstrap_ats_template.format(**args)
    logging.info(cmd)

    return utils.run_cmd('bootstrap', module_name, cmd)
        



