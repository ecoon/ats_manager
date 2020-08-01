"""Sets up and runs bootstrap"""
import os,stat
import subprocess
import logging
import ats_manager.names as names
import ats_manager.utils as utils

def bootstrapExistingFromFile(module_name):
    return utils.run_script('bootstrap', module_name)


def _set_arg(args, key, val):
    if val:
        args[key] = 'enable'
    else:
        args[key] = 'disable'
        

_bootstrap_amanzi_template = \
"""#!/bin/env bash
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
    --${{AMANZI_TRILINOS_BUILD_TYPE}}_trilinos \
    --${{AMANZI_TPLS_BUILD_TYPE}}_tpls \
    --parallel=8 \
    --enable-shared \
    --tpl-build-dir=${{AMANZI_TPLS_BUILD_DIR}} \
    --tpl-install-prefix=${{AMANZI_TPLS_DIR}} \
    --amanzi-build-dir=${{AMANZI_BUILD_DIR}} \
    --amanzi-install-prefix=${{AMANZI_DIR}} \
    --tools-build-dir=${{ATS_BASE}}/tools/build-1 \
    --tools-install-prefix=${{ATS_BASE}}/tools/install-1 \
    --tools-download-dir=${{ATS_BASE}}/tools/Downloads \
    --tpl-download-dir=${{ATS_BASE}}/amanzi-tpls/Downloads {tpl_config_file} \
    --{structured}-structured \
    --{geochemistry}-geochemistry \
    --{geochemistry}-petsc \
    --{geochemistry}-alquimia \
    --{geochemistry}-pflotran \
    --{geochemistry}-crunchtope \
    --enable-amanzi_physics \
    --enable-hypre \
    --enable-silo \
    --enable-clm \
    --disable-ats_physics \
    --with-mpi=${{MPI_DIR}} \
    --tools-mpi=openmpi \
    --with-c-compiler=`which mpicc` \
    --with-cxx-compiler=`which mpicxx` \
    --with-fort-compiler=`which mpifort`

exit $?
""" 
def bootstrap_amanzi(module_name,
                     enable_structured=False,
                     enable_geochemistry=True,
                     use_existing_tpls=False):
    args = dict()
    args['module_name'] = module_name
    _set_arg(args, 'structured', enable_structured)
    _set_arg(args, 'geochemistry', enable_geochemistry)

    if use_existing_tpls:
        args['tpl_config_file'] = "    --tpl-config-file=${AMANZI_TPLS_DIR}/share/cmake/amanzi-tpl-config.cmake"
    else:
        args['tpl_config_file'] = ""

    logging.info('Filling  bootstrap')
    logging.info(args)
    cmd = _bootstrap_amanzi_template.format(**args)
    logging.info(cmd)
    
    return utils.run_cmd('bootstrap', module_name, cmd)
        

_bootstrap_ats_template = \
"""#!/bin/env bash
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
    --${{AMANZI_TRILINOS_BUILD_TYPE}}_trilinos \
    --${{AMANZI_TPLS_BUILD_TYPE}}_tpls \
    --parallel=8 \
    --enable-shared \
    --tpl-build-dir=${{AMANZI_TPLS_BUILD_DIR}} \
    --tpl-install-prefix=${{AMANZI_TPLS_DIR}} \
    --amanzi-build-dir=${{AMANZI_BUILD_DIR}} \
    --amanzi-install-prefix=${{AMANZI_DIR}} \
    --tools-build-dir=${{ATS_BASE}}/tools/build-1 \
    --tools-install-prefix=${{ATS_BASE}}/tools/install-1 \
    --tools-download-dir=${{ATS_BASE}}/tools/Downloads \
    --tpl-download-dir=${{ATS_BASE}}/amanzi-tpls/Downloads {tpl_config_file} \
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
    --ats_dev \
    --with-mpi=${{MPI_DIR}} \
    --tools-mpi=openmpi \
    --with-c-compiler=`which mpicc` \
    --with-cxx-compiler=`which mpicxx` \
    --with-fort-compiler=`which mpifort`

exit $?
""" 
def bootstrap_ats(module_name,
                 enable_geochemistry=False,
                 use_existing_tpls=False):
    args = dict()
    args['module_name'] = module_name
    _set_arg(args, 'geochemistry', enable_geochemistry)

    if use_existing_tpls:
        args['tpl_config_file'] = "    --tpl-config-file=${AMANZI_TPLS_DIR}/share/cmake/amanzi-tpl-config.cmake"
    else:
        args['tpl_config_file'] = ""
    
    logging.info('Filling bootstrap command:')
    logging.info(args)
    cmd = _bootstrap_ats_template.format(**args)
    logging.info(cmd)

    return utils.run_cmd('bootstrap', module_name, cmd)
        


