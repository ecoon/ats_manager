import argparse
import sys,os
import logging

import ats_manager.names as names

def fill_template(file_in, file_out, substitutions):
    """Fills a python template file and writes it to disk."""
    logging.info("Writing template: {}".format(file_in))
    logging.info(" to: {}".format(file_out))
    logging.info(" using substitutions:")
    for key,val in substitutions.items():
        logging.info("  {} : {}".format(key,val))

    with open(file_in,'r') as fin:
        template = fin.read()
    modfile = template.format(**substitutions)
    with open(file_out, 'w') as fout:
        fout.write(modfile)
    return


def tpls_modulefile_args(tpls_name,
                         repo_kind,
                         repo_version,
                         tpls_build_type='opt',
                         trilinos_build_type='opt',
                         modulefiles=None,
                         **kwargs):
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
                    build_type='opt',
                    **kwargs):
    temp_pars = dict()
    temp_pars['amanzi'] = name
    temp_pars['build_type'] = build_type
    temp_pars['tpls_modulefile'] = tpls_modulefile
    temp_pars['amanzi_src_dir'] = names.amanzi_src_dir(repo_version)
    temp_pars['amanzi_build_dir'] = names.amanzi_build_dir(name)
    temp_pars['amanzi_dir'] = names.amanzi_install_dir(name)

    if kind == 'ats':
        temp_pars['ats'] = name
        temp_pars['ats_src_dir'] = names.ats_src_dir(repo_version)
        temp_pars['ats_regression_tests_dir'] = names.ats_regression_tests_dir(name)
    return temp_pars
    

def _template_path(kind):
    """Returns the name of the template to be filled."""
    return os.path.join(os.environ['ATS_BASE'],'ats_manager','share',
                            'templates',f'{kind}_modulefile.template')


def create_tpls_modulefile(tpls_name, repo_name, **kwargs):
    """Sets up the name of the modulefile to be created.  Note this also
    creates the subdirectory containing that file, if needed."""
    outfile = names.modulefile_path(tpls_name)
    outfile_dir = os.path.join(*os.path.split(outfile)[:-1])
    os.makedirs(outfile_dir, exist_ok=True)

    temp_pars = tpls_modulefile_args(tpls_name, repo_name, **kwargs)
    template = _template_path('tpls')

    fill_template(template, outfile, temp_pars)
    return temp_pars


def create_modulefile(name, repo_version, tpls_name, **kwargs):
    """Sets up the name of the modulefile to be created.  Note this also
    creates the subdirectory containing that file, if needed."""
    outfile = names.modulefile_path(name)
    outfile_dir = os.path.join(*os.path.split(outfile)[:-1])
    os.makedirs(outfile_dir, exist_ok=True)

    kind = name.split('/')[0]
    temp_pars = modulefile_args(kind, name, repo_version, tpls_name, **kwargs)
    template = _template_path(kind)

    fill_template(template, outfile, temp_pars)
    return temp_pars
