#===============================================================================
# download.py
#===============================================================================

# Imports ======================================================================

import os
import os.path
import subprocess

from argparse import ArgumentParser
from hashlib import sha256
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from wasp_map.env import ANACONDA_DIR, DIR




# Constants ====================================================================

ANACONDA_URL = os.environ.get(
    'WASP_MAP_ANACONDA_URL',
    'https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh'
)
ANACONDA_HASH = os.environ.get(
    'WASP_MAP_ANACONDA_HASH',
    '45c851b7497cc14d5ca060064394569f724b67d9b5f98a926ed49b834a6bb73a'
)




# Functions ====================================================================

def download_anaconda_install_script(anaconda_install_script_path, quiet=False):
    if not quiet:
        print(
            'Downloading Anaconda3 install script to '
            f'{anaconda_install_script_path}'
        )
    with urlopen(ANACONDA_URL) as (
        response
    ), open(anaconda_install_script_path, 'wb') as (
        f
    ):
        copyfileobj(response, f)


def check_hash(anaconda_install_script_path, quiet=False):
    if not quiet:
        print(f'checking hash of {anaconda_install_script_path}')
    with open(anaconda_install_script_path, 'rb') as f:
        if sha256(f.read()).hexdigest() != ANACONDA_HASH:
            raise RuntimeError(f'hash check failed for {ANACONDA_URL}')


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
    if os.path.isdir(ANACONDA_DIR):
        use_existing_dir = input(
            f'There is already a directory at {ANACONDA_DIR} - is this the '
            'anaconda you wish to use? (Y/n) >>>'
        )
        if use_existing_dir not in {'', 'y', 'Y'}:
            print(
                'Please change the value of environment variable '
                'WASP_MAP_ANACONDA_DIR'
            )
            return
    elif os.path.exists(ANACONDA_DIR):
        raise RuntimeError(f'There is a non-directory file at {ANACONDA_DIR}')
    with TemporaryDirectory(dir=args.tmp_dir) as temp_dir:
        anaconda_install_script_path = os.path.join(
            temp_dir, 'Anaconda3-2019.03-Linux-x86_64.sh'
        )
        download_anaconda_install_script(
            anaconda_install_script_path,
            quiet=args.quiet
        )
        check_hash(anaconda_install_script_path, quiet=args.quiet)
        input(
            'installing Anaconda3. When prompted, specify the following '
            f'install location:\n{ANACONDA_DIR}\n\npress ENTER to '
            'continue >>>'
        )
        subprocess.run(('bash', anaconda_install_script_path))
