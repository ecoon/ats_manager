import sys
import argparse
import ats_manager as manager

def get_args():
    parser = argparse.ArgumentParser('Install Amanzi TPLs from a branch.')
    parser, groups = manager.get_install_args(parser, False)
    args = parser.parse_args()
    manager.set_default_args(args)
    return args

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    args = vars(get_args())
    args['modulefiles'] = args.pop('modulefile')
    rc, module = manager.install_tpls(**args)
    sys.exit(rc)
    
