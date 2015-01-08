# This file is part of masbpy.

# masbpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# masbpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with masbpy.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2014 Ravi Peters

import os
import numpy as np

def write_npy(dir, datadict):
	if not os.path.exists(dir):
	    os.makedirs(dir)

	for key,val in datadict.items():
		fname = os.path.join(dir,key)
		np.save(fname, val)

def read_npy(dir, keys):
	assert os.path.exists(dir)

	datadict = {}	
	for key in keys:
		fname = os.path.join(dir,key+'.npy')
		if os.path.exists(fname):
			datadict[key] = np.load(fname)
	return datadict


# dtypes = dict()
# # see http://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.html#numpy.dtype
# dtypes['coords'] = np.dtype([('coords', '3<f4')])
# dtypes['normals'] = np.dtype([('normals', '3<f4')])
# dtypes['ma_coords_in'] = np.dtype([('ma_coords_in', '3<f4')])
# dtypes['ma_coords_out'] = np.dtype([('ma_coords_out', '3<f4')])
# dtypes['lfs'] = np.dtype([('lfs', '<f8')])

# def write_bin(datadict, dir):
# 	if not os.path.exists(dir):
# 	    os.makedirs(dir)

# 	for key,val in datadict.items():
# 		if dtypes.has_key(key):
# 			fname = os.path.join(dir,key)
# 			val.tofile(fname)

# def read_bin(dir):
# 	datadict = {}
# 	for name, dtype in dtypes.items():
# 		fname = os.path.join(dir,name)
# 		datadict[name] = np.fromfile(fname, dtype=dtype)
# 	return datadict
