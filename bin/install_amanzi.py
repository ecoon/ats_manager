import sys
import argparse
import ats_manager

def get_args():
    parser = argparse.ArgumentParser('Install Amanzi from a branch.')
    parser, groups = ats_manager.get_install_args(parser, amanzi=True)
    args = parser.parse_args()
    args.modulefiles = args.modulefile
    args.enable_geochemistry = not args.disable_geochemistry
    del(args.modulefile)
    return args


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    args = get_args()
    rc, module = ats_manager.install_amanzi(args)
    sys.exit(rc)
    
