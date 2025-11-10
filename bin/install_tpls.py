import sys
import argparse
import ats_manager

def get_args():
    parser = argparse.ArgumentParser('Install Amanzi TPLs from a branch.')
    parser, groups = manager.get_install_tpls_args(parser)
    args = parser.parse_args()

    args.modulefiles = args.modulefile
    del(args.modulefile)

    args.repo_kind = 'amanzi'
    return args

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    args = get_args()
    rc, module = manager.install_tpls(args)
    sys.exit(rc)
    
