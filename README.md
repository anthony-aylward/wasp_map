# wasp_map
Utilites for the mapping pipeline from [WASP](https://github.com/bmvdgeijn/WASP)

## Installation

**Step 0 (optional):** If you wish to specify the locations of the Anaconda3
and/or WASP installations, you can do so through the environment variables
`WASP_MAP_ANACONDA_DIR` and `WASP_MAP_DIR`. For example, you could append this
to your `.bash_profile`:
```sh
export WASP_MAP_ANACONDA_DIR=~/anaconda3
export WASP_MAP_DIR=~/WASP
```

If these environment variables point to already-existing installations of
Anaconda3 and WASP, respectively, then you can skip step 2 (running
`wasp_map-download`).

If you also set environment variable `LD_LIBRARY_PATH` appropriately, you can
skip step 3 (running `wasp_map-set-ldlib`). For example:

```sh
export WASP_MAP_ANACONDA_DIR=~/anaconda3
export WASP_MAP_DIR=~/WASP
export LD_LIBRARY_PATH=${WASP_MAP_ANACONDA_DIR}/lib:$LD_LIBRARY_PATH
```

**Step 1:** install the python package via `pip3`:
```sh
pip3 install wasp_map
```
or
```sh
pip3 install --user wasp_map
```

**Step 2:** Once the python package is installed, run
```sh
wasp_map-download
```
and follow the prompts. Anaconda3 and/or WASP will be installed, if necessary.

**Step 3:** Next, run
```sh
wasp_map-set-ldlib
```
and follow the instruction. It will be something like:
```
Run the following `export` command, or append it to your .bashrc, .profile, or .bash_profile:
export LD_LIBRARY_PATH=/home/aaylward/.local/lib/python3.6/site-packages/wasp_map/anaconda3/lib:$LD_LIBRARY_PATH
```
