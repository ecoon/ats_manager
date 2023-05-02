import sys
import argparse
import ats_manager

def get_args():
    parser = argparse.ArgumentParser('Install Amanzi from a branch.')
    parser, groups = manager.get_install_args(parser, amanzi=True)
    args = parser.parse_args()
    args.modulefiles = args.modulefile
    del(args.modulefile)
    return args


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    args = get_args()
    rc, module = manager.install_amanzi(args)
    sys.exit(rc)
    
