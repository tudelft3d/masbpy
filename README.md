**This project is outdated. Please use [masbcpp](http://github.com/tudelft3d/masbcpp), a much faster and more robust C++ implementation.**
# masbpy
masbpy is a python implementation of the shrinking ball algorithm to approximate the Medial Axis Transform (MAT) of an oriented point cloud. It is being developed in support of the [3DSM project](http://3dgeoinfo.bk.tudelft.nl/projects/3dsm/) that aims to explore possible applications of the MAT for GIS point clouds (e.g. from airborne [LiDAR](http://en.wikipedia.org/wiki/Lidar)). To deal with noisy input data a noise-handling mechanism is built-in.

[This video](https://vimeo.com/84859998) demonstrates how the shrinking ball algorithm works using an early version of masbpy.

## Installation
Succesfull installations have been reported for both Linux and Mac OS X platforms. Installation should be as simple as

```
$ git clone https://github.com/tudelft3d/masbpy.git
$ cd masbpy
$ python setup.py install
```
or simply
```
$ pip install git+https://github.com/tudelft3d/masbpy.git
```
This should automatically install all required dependencies. 

Minimal dependencies:
* numpy [http://www.numpy.org]
* pykdtree [https://github.com/storpipfugl/pykdtree]

Optional dependecies:
* numba (faster computation) [http://numba.pydata.org]
* laspy (read las files) [https://github.com/grantbrown/laspy]
* scikit-learn (to approximate normals) [http://scikit-learn.org/stable/index.html]

## Usage
Provided is an example script `example.py` that demonstrate how to use this library to approximate the MAT of an example dataset that is also provided. The easiest way to get started however, is to use the provided `compute_ma.py` utility.

Supported input formats are currently: `_npy`, `.ply` and `.las` (if laspy is installed). Note that point normals must be present, if this is not the case these can be approximated using the provided `compute_normals.py` utility.

Internally masbpy uses numpy arays. These can be conveniently stored as binary files, which is also the fastest way to read and write input and output with masbpy. It is actually also the only way to store masbpy outputs now. To use this format append `_npy` to you in- and output specifiers.

For example this is how to approximate the MAT from a LAS file.

```
$ compute_normals.py my_data.las my_data_npy
$ compute_ma.py my_data_npy my_data_npy
```
You will now have a directory `my_data_npy` with a number of `.npy` files that each correspond to a numpy array. Most notable are `ma_coords_in.npy` and `ma_coords_out.npy`; these contain the in- and exterior approximate MAT points. You can access these as follows from a python shell:

```
> from masbpy import io_npy
> datadict = io_npy.read_npy('my_data_npy', ['ma_coords_in', 'ma_coords_out'])
> datadict['ma_coords_in']
array([[ 4.66304016,  6.7078476 , -0.62416261],
       [ 4.66304016,  6.17656088,  0.72636408],
       [ 4.66304016,  5.91777468,  1.28132153],
       ..., 
       [ 0.63925803,  0.89763576,  0.92685151],
       [ 1.80165005,  0.89763576,  0.92685151],
       [-0.90879714, -0.8976357 ,  0.92685151]], dtype=float32)
```

## Limitations
The current implementation is not infinitely scalable, mainly in terms of memory usage. Processing very large datasets (hundreds of millions of points or more) is therefore not really supported. 

## Acknowledgements
The shinking ball algorithm was originally introduced by [ma12]

```bib
@article{ma12,
  title={3D medial axis point approximation using nearest neighbors and the normal field},
  author={Ma, Jaehwan and Bae, Sang Won and Choi, Sunghee},
  journal={The Visual Computer},
  volume={28},
  number={1},
  pages={7--19},
  year={2012},
  publisher={Springer}
}
```
see http://gclab.kaist.ac.kr/publications/VC2011.pdf
