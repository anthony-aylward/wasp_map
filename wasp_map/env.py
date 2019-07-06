#===============================================================================
# env.py
#===============================================================================

import os
import os.path

ANACONDA_DIR = os.environ.get(
    'WASP_MAP_ANACONDA_DIR',
    os.path.join(os.path.dirname(__file__), 'anaconda3')
)
DIR = os.environ.get(
    'WASP_MAP_DIR',
    os.path.join(os.path.dirname(__file__), 'WASP')
)
