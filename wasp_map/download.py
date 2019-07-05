#===============================================================================
# download.py
#===============================================================================

# Imports ======================================================================

from argparse import ArgumentParser

from wasp_map.env import ANACONDA_DIR, DIR




# Functions ====================================================================

def parse_arguments():
    parser = ArgumentParser(description='download and install WASP')
    parser.add_argument(
      '--quiet',
      action='store_true',
      help='suppress status updates'
    )
    return parser.parse_args()
