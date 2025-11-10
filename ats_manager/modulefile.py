import argparse
import sys,os
import logging

import ats_manager.names as names
import ats_manager.utils as utils
from ats_manager.config import config

#
# Templates
#
_ats_template = \
"""#%Module1.0#####################################################################
##
## modules modulefile
##
proc ModulesHelp {{ }} {{
    global mpi_bin

    puts stderr "\tATS {ats} repository, {build_type} build"
    puts stderr ""
}}

module-whatis   "ATS {ats} {build_type} build"
# #############################################################################

module load {tpls_modulefile}

setenv AMANZI_SRC_DIR {amanzi_src_dir}
setenv AMANZI_BUILD_DIR {amanzi_build_dir}
setenv AMANZI_DIR {amanzi_dir}

setenv ATS_SRC_DIR {ats_src_dir}
setenv ATS_BUILD_DIR {amanzi_build_dir}
setenv ATS_DIR {amanzi_dir}

setenv ATS_TESTS_DIR {ats_regression_tests_dir}

setenv AMANZI_BUILD_TYPE {build_type}

prepend-path    PATH            {amanzi_dir}/bin
prepend-path    PYTHONPATH      {amanzi_src_dir}/tools/amanzi_xml
prepend-path    PYTHONPATH      {ats_src_dir}/tools/utils
prepend-path    PYTHONPATH      {ats_src_dir}/tools/ats_meshing/ats_meshing
"""


_amanzi_template = \
"""#%Module1.0#####################################################################
##
## modules modulefile
##
proc ModulesHelp {{ }} {{
    puts stderr "\tAmanzi {amanzi} repository, {build_type} build"
    puts stderr ""
}}

module-whatis   "Amanzi {amanzi} {build_type} build"
# #############################################################################

module load {tpls_modulefile}

setenv AMANZI_SRC_DIR {amanzi_src_dir}
setenv AMANZI_BUILD_DIR {amanzi_build_dir}
setenv AMANZI_DIR {amanzi_dir}

setenv AMANZI_BUILD_TYPE {build_type}

prepend-path    PATH            {amanzi_dir}/bin
prepend-path    PYTHONPATH      {amanzi_src_dir}/tools/amanzi_xml
"""    

_tpls_template = \
"""#%Module1.0#####################################################################
##
## modules modulefile
##
proc ModulesHelp {{ }} {{
    puts stderr "\tAmanzi TPLs {amanzi} repository, {tpls_build_type} build"
    puts stderr ""
}}

module-whatis   "Amanzi TPLs {amanzi} {tpls_build_type} build"
# #############################################################################

{modulefiles}

setenv AMANZI_TPLS_DIR {tpls_dir}
setenv AMANZI_TPLS_BUILD_DIR {tpls_build_dir}
setenv AMANZI_TPLS_SOURCE_DIR {tpls_src_dir}
setenv AMANZI_TPLS_CONFIG {tpls_dir}/share/cmake/amanzi-tpl-config.cmake

setenv AMANZI_TPLS_BUILD_TYPE {tpls_build_type}
setenv AMANZI_TRILINOS_BUILD_TYPE {trilinos_build_type}

prepend-path    PATH            {tpls_dir}/bin
prepend-path    PYTHONPATH      {tpls_dir}/SEACAS/lib
"""


def fill_template(template, file_out, substitutions):
    """Fills a python template file and writes it to disk."""
    logging.info("Writing template to: {}".format(file_out))
    logging.info(" using substitutions:")
    for key,val in substitutions.items():
        logging.info("  {} : {}".format(key,val))

    modfile = template.format(**substitutions)
    with open(file_out, 'w') as fout:
        fout.write(modfile)

    utils.chmod(file_out)
    return


def tpls_modulefile_args(tpls_name,
                         repo_kind,
                         repo_version,
                         tpls_build_type='opt',
                         trilinos_build_type='opt',
                         modulefiles=None):
    temp_pars = dict()
    temp_pars['amanzi'] = tpls_name
    temp_pars['tpls_build_type'] = tpls_build_type
    temp_pars['trilinos_build_type'] = trilinos_build_type

    if modulefiles is not None:
        temp_pars['modulefiles'] = '\n'.join(['module load {}'.format(mf) for mf in modulefiles])
    else:
        temp_pars['modulefiles'] = ''

    temp_pars['tpls_src_dir'] = names.amanzi_src_dir(repo_kind,repo_version)
    temp_pars['tpls_build_dir'] = names.build_dir(tpls_name)    
    temp_pars['tpls_dir'] = names.install_dir(tpls_name)
    return temp_pars
    

def modulefile_args(kind,
                    name,
                    repo_version,
                    tpls_modulefile,
                    build_type='opt'):
    temp_pars = dict()
    temp_pars['amanzi'] = name
    temp_pars['build_type'] = build_type
    temp_pars['tpls_modulefile'] = tpls_modulefile
    temp_pars['amanzi_src_dir'] = names.amanzi_src_dir(kind, repo_version)
    temp_pars['amanzi_build_dir'] = names.build_dir(name)
    temp_pars['amanzi_dir'] = names.install_dir(name)

    if kind == 'ats':
        temp_pars['ats'] = name
        temp_pars['ats_src_dir'] = names.ats_src_dir(repo_version)
        temp_pars['ats_regression_tests_dir'] = names.ats_regression_tests_dir(name)
    return temp_pars
    

def _template_path(kind):
    """Returns the name of the template to be filled."""
    return os.path.join(os.environ['ATS_BASE'],'ats_manager','share',
                            'templates',f'{kind}_modulefile.template')


def create_tpls_modulefile(tpls_name, repo_kind, repo_version, **kwargs):
    """Sets up the name of the modulefile to be created.  Note this also
    creates the subdirectory containing that file, if needed."""
    outfile = names.modulefile_path(tpls_name)
    outfile_dir = os.path.join(*os.path.split(outfile)[:-1])
    os.makedirs(outfile_dir, exist_ok=True)

    temp_pars = tpls_modulefile_args(tpls_name, repo_kind, repo_version, **kwargs)
    fill_template(_tpls_template, outfile, temp_pars)
    return temp_pars


def create_modulefile(name, repo_version, tpls_name, **kwargs):
    """Sets up the name of the modulefile to be created.  Note this also
    creates the subdirectory containing that file, if needed."""
    outfile = names.modulefile_path(name)
    outfile_dir = os.path.join(*os.path.split(outfile)[:-1])
    os.makedirs(outfile_dir, exist_ok=True)

    kind = name.split('/')[0]
    temp_pars = modulefile_args(kind, name, repo_version, tpls_name, **kwargs)

    if kind == 'ats':
        template = _ats_template
    elif kind == 'amanzi':
        template = _amanzi_template

    fill_template(template, outfile, temp_pars)
    return temp_pars
