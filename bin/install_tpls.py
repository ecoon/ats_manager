import sys
import argparse
import ats_manager

def get_args():
    parser = argparse.ArgumentParser('Install Amanzi TPLs from a branch.')
    parser, groups = ats_manager.get_install_args(parser)
    args = parser.parse_args()

    args.modulefiles = args.modulefile
    del(args.modulefile)
    return args

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    args = get_args()
    rc, module = ats_manager.check_or_install_tpls(args)
    sys.exit(rc)
    
