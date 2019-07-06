#===============================================================================
# download.py
#===============================================================================

# Imports ======================================================================

import os
import os.path
import subprocess

from argparse import ArgumentParser
from git import Git
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
CONDA_PATH = os.path.join(ANACONDA_DIR, 'bin', 'conda')
WASP_GITHUB_REPO = 'https://github.com/bmvdgeijn/WASP.git'




# Functions ====================================================================

def download_anaconda_install_script(anaconda_install_script_path):
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


def check_hash(anaconda_install_script_path):
    print(f'checking hash of {anaconda_install_script_path}')
    with open(anaconda_install_script_path, 'rb') as f:
        if sha256(f.read()).hexdigest() != ANACONDA_HASH:
            raise RuntimeError(f'hash check failed for {ANACONDA_URL}')


def install_anaconda(anaconda_install_script_path):
    input(
        'installing Anaconda3. When prompted, specify the following '
        f'install location:\n{ANACONDA_DIR}\npress ENTER to '
        'continue >>>'
    )
    subprocess.run(('bash', anaconda_install_script_path))


def configure_anaconda():
    print('configuring Anaconda3')
    subprocess.run((CONDA_PATH, 'config', '--add', 'channels', 'r'))
    subprocess.run((CONDA_PATH, 'config', '--add', 'channels', 'bioconda'))
    subprocess.run((CONDA_PATH, 'install', 'pysam'))


def clone_wasp():
    print(
        'cloning the WASP github repo to '
        f"{os.path.join(os.path.dirname(DIR), 'WASP')}"
    )
    Git(os.path.dirname(DIR)).clone(WASP_GITHUB_REPO)


def parse_arguments():
    parser = ArgumentParser(description='download and install WASP')
    parser.add_argument(
        '--tmp-dir',
        metavar='<dir/for/temp/files>',
        help='directory to use for temporary files'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    if os.path.isdir(ANACONDA_DIR):
        use_existing_anaconda_dir = (
            input(
                f'There is already a directory at {ANACONDA_DIR} - is this the '
                'anaconda you wish to use? ([y]/n) >>>'
            ).casefold()
            in {'', 'y', 'yes'}
        )
        if not use_existing_anaconda_dir:
            print(
                'Please change the value of environment variable '
                'WASP_MAP_ANACONDA_DIR or remove the existing directory at '
                'that location.'
            )
            return
    elif os.path.exists(ANACONDA_DIR):
        raise RuntimeError(
            f'There is a non-directory file at {ANACONDA_DIR}. Please change '
            'the value of environment variable WASP_MAP_ANACONDA_DIR or '
            'remove the existing file at that location.'
        )
    else:
        use_existing_anaconda_dir = False
    if os.path.isdir(DIR):
        use_existing_wasp_dir = (
            input(
                f'There is already a directory at {DIR} - is this the '
                'WASP you wish to use? ([y]/n) >>>'
            ).casefold() in {'', 'y', 'yes'}
        )
        if not use_existing_wasp_dir:
            print(
                'Please change the value of environment variable WASP_MAP_DIR '
                'or remove the existing directory at that location.'
            )
            return
    elif os.path.exists(DIR):
        raise RuntimeError(
            f'There is a non-directory file at {DIR} Please change '
            'the value of environment variable WASP_MAP_DIR or '
            'remove the existing file at that location.'
        )
    else:
        use_existing_wasp_dir = False
    
    with TemporaryDirectory(dir=args.tmp_dir) as temp_dir:
        anaconda_install_script_path = os.path.join(
            temp_dir, 'Anaconda3-2019.03-Linux-x86_64.sh'
        )
        download_anaconda_install_script(anaconda_install_script_path)
        check_hash(anaconda_install_script_path)
        install_anaconda(anaconda_install_script_path)
    configure_anaconda()
    if not use_existing_wasp_dir:
        clone_wasp()
