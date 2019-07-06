#===============================================================================
# download.py
#===============================================================================

# Imports ======================================================================

import hashlib
import os.path

from argparse import ArgumentParser
from urllib.request import urlopen
from shutil import copyfileobj
from subprocess import run
from tempfile import TemporaryDirectory

from wasp_map.env import ANACONDA_DIR, DIR




# Constants ====================================================================

ANACONDA_URL = (
    'https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh'
)




# Functions ====================================================================

def parse_arguments():
    parser = ArgumentParser(description='download and install WASP')
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='suppress status updates'
    )
    parser.add_argument(
        '--tmp-dir',
        metavar='<dir/for/temp/files>',
        help='directory to use for temporary files'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    if os.path.exists(ANACONDA_DIR):
        raise RuntimeError(f'There is already a file at {ANACONDA_DIR}')
    with TemporaryDirectory(dir=args.tmp_dir) as temp_dir:
        anaconda_install_script_path = os.path.join(
            temp_dir, 'Anaconda3-2019.03-Linux-x86_64.sh'
        )
        if not args.quiet:
            print(
                'Downloading Anaconda install script to '
                f'{anaconda_install_script_path}'
            )
        with urlopen(ANACONDA_URL) as (
            response
        ), open(anaconda_install_script_path, 'wb') as (
            f
        ):
            copyfileobj(response, f)
        m = hashlib.sha256()
        with open(anaconda_install_script_path, 'rb') as f:
            m.update(f.read())
        print(m.digest().decode())
        # run('bash', anaconda_install_script_path)
        

