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