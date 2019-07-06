#===============================================================================
# ldlib.py
#===============================================================================

# Imports ======================================================================

import os
import os.path

from subprocess import run

from wasp_map.env import ANACONDA_DIR




# Functions ====================================================================

def main():
    command = (
        'export '
        'LD_LIBRARY_PATH='
        f"{os.path.join(ANACONDA_DIR, 'lib')}:$LD_LIBRARY_PATH"
    )
    print(
        'Run the following `export` command, or append it to your .bashrc, '
        f'.profile, or .bash_profile:\n{command}'
    )
