from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
Extension('algebra', ['masbpy/algebra.pyx'], include_dirs=[np.get_include()], libraries=["m"])
# Extension('ma_mp_cy', ['masbpy/ma_mp.pyx'], include_dirs=[np.get_include()], libraries=["m"])
]

setup(
    name = "masbpy",
    version = "0.1",
    packages = find_packages(),
    install_requires = ["numpy>=1.9.1", "pykdtree>=0.2"],
    ext_modules = cythonize(extensions),
    extras_require = {
        'LAS':  ["laspy"],
        'numba': ["numba"],
    },
    scripts = ['util/compute_ma.py', 'util/compute_normals.py']
)