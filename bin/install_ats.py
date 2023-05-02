import sys
import argparse
import ats_manager

def get_args():
    parser = argparse.ArgumentParser('Install ATS from a branch.')
    ats_manager.get_install_args(parser, ats=True)
    args = parser.parse_args()
    args.modulefiles = args.modulefile
    del(args.modulefile)
    return args
    

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    args = get_args()
    rc, module = ats_manager.install_ats(args)
    sys.exit(rc)
    
