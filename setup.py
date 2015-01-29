from setuptools import setup, find_packages
setup(
    name = "masbpy",
    version = "0.1",
    packages = find_packages(),
    install_requires = ["numpy>=1.9.1", "pykdtree>=0.2"],
    extras_require = {
        'LAS':  ["laspy"],
        'numba': ["numba"],
    },
    scripts = ['util/compute_ma.py', 'util/compute_normals.py']
)