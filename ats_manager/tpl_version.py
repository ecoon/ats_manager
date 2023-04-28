"""Determines TPL versions from Amanzi"""
import os

def _find_version(fid, kind):
    startstr = f'set(AMANZI_TPLS_VERSION_{kind.upper()}'
    line = next(l.strip() for l in fid if l.strip().startswith(startstr))
    line = line[len(startstr):].strip()
    version = line.split(')')[0].strip()
    return version
    
    
def find_tpl_version(amanzi_dir):
    """Given an Amanzi directory, find the TPLs version number."""
    tpl_versions_file = os.path.join(amanzi_dir, 'config', 'SuperBuild', 'TPLVersions.cmake')
    with open(tpl_versions_file, 'r') as fid:
        major = _find_version(fid, 'major')
        minor = _find_version(fid, 'minor')
        patch = _find_version(fid, 'patch')
    return '.'.join([major,minor,patch])

        
                     
