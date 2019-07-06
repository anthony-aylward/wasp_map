import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wasp_map',
    version='0.0.4',
    author='Anthony Aylward',
    author_email='aaylward@eng.ucsd.edu',
    description='Utilites for the mapping pipeline from WASP',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/wasp_map.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[],
    entry_points={
        'console_scripts': ['wasp_map-download=wasp_map.download:main',]
    }
)
