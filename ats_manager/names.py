import os

_amanzi_url_template = 'https://github.com/amanzi/{}.git'
amanzi_url = _amanzi_url_template.format('amanzi')
ats_url = _amanzi_url_template.format('ats')
ats_regression_tests_url = _amanzi_url_template.format('ats-regression-tests')
ats_demos_url = _amanzi_url_template.format('ats-demos')
valid_build_types = ['debug', 'opt', 'relwithdebinfo']
ats_submodule = 'src/physics/ats'

def _clean(instr):
    outstr = instr.replace('/', '-')
    outstr = outstr.replace(' ', '_')
    return outstr


def _find_version(fid, kind):
    startstr = f'set(AMANZI_TPLS_VERSION_{kind.upper()}'
    line = next(l.strip() for l in fid if l.strip().startswith(startstr))
    line = line[len(startstr):].strip()
    version = line.split(')')[0].strip()
    return version
    
    
# paths to useful places
def amanzi_src_dir(kind, version):
    return os.path.join(os.environ['ATS_BASE'], kind, 'repos', version)

def ats_src_dir(version):
    return os.path.join(amanzi_src_dir('ats', version), 'src', 'physics', 'ats')

def tpls_src_dir(kind, version):
    return os.path.join(amanzi_src_dir(kind, version), 'config', 'SuperBuild')

def ats_regression_tests_dir(version):
    return os.path.join(ats_src_dir('ats', version), 'testing', 'ats-regression-tests')

def tools_mpi_dir(vendor):
    return os.path.join(os.environ['ATS_BASE'], 'tools', 'install', vendor)

def tpls_version(kind, version):
    """Given an Amanzi or ATS version, find the TPLs version."""
    tpl_versions_file = os.path.join(tpls_src_dir(kind, version), 'TPLVersions.cmake')
    with open(tpl_versions_file, 'r') as fid:
        major = _find_version(fid, 'major')
        minor = _find_version(fid, 'minor')
        patch = _find_version(fid, 'patch')
    return f'{major}.{minor}.{patch}'

# names are fully qualified combination of kind, version, machine,
# compilers, and build type
def name(kind, version, machine, compilers, build_type):
    """Returns a unique name for identifying installations."""
    arglist = [_clean(kind), _clean(version)]

    if machine is not None: arglist.append(_clean(machine))
    if compilers is not None: arglist.append(_clean(compilers))
    if build_type is not None: arglist.append(_clean(build_type))

    return os.path.join(arglist)
        
def install_dir(name):
    name_trip = name.split('/')
    args = [os.environ['ATS_BASE'], name_trip[0], 'install'] + name_trip[1:]
    return os.path.join(*args)

def build_dir(name):
    name_trip = name.split('/')
    args = [os.environ['ATS_BASE'], name_trip[0], 'build'] + name_trip[1:]
    return os.path.join(*args)

def modulefile_path(name):
    return os.path.join(os.environ['ATS_BASE'], 'modulefiles', name)



