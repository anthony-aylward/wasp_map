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
        'export',
        f"LD_LIBRARY_PATH={os.path.join(ANACONDA_DIR, 'lib')}:$LD_LIBRARY_PATH"
    )
    run(command)
    print(
        f"The following `export` command was run:\n{' '.join(command)}\n"
        'To avoid repeating this step, append the above command to your '
        '.bashrc, .profile, or .bash_profile'
    )
