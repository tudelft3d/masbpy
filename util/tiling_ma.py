import glob
from multiprocessing import Pool
from time import time

import laspy
import numpy as np
from masbpy.ma_mp import MASB
from masbpy import io_npy

import pcl

las_tiles = glob.glob('/Volumes/HFS2000/*.las')
tile_size = 750
buf = 100
k = 10


for las_file_path in las_tiles:
	npy_file_path = las_file_path[:-4]+'_npy'

	las_file = laspy.file.File(las_file_path)

	
	# get bounding box without buffer
	bb_min = las_file.header.get_min()
	bb_max = las_file.header.get_max()
	bb_min[0] += buf
	bb_min[1] += buf
	bb_max[0] -= buf
	bb_max[1] -= buf
	center_x = 0#(bb_max[0] - bb_min[0])/2
	center_y = 0#(bb_max[1] - bb_min[1])/2

	# seperate points inside and outside bufferless bounding box
	x_inside_mask = np.logical_and(np.greater(las_file.x, bb_min[0]), np.less(las_file.x, bb_max[0]))
	y_inside_mask = np.logical_and(np.greater(las_file.y, bb_min[1]), np.less(las_file.y, bb_max[1]))
	inside_mask = np.logical_and(x_inside_mask, y_inside_mask)

	datadict = {}
	datadict['coords'] = np.column_stack([ np.array(a[inside_mask], dtype=np.float32) for a in [las_file.x-center_x, las_file.y-center_y, las_file.z] ])
	datadict['coords_in_buffer'] = np.column_stack([ np.array(a[~inside_mask], dtype=np.float32) for a in [las_file.x-center_x, las_file.y-center_y, las_file.z] ])

	# creat MASB object, so that also KDtree gets created
	ma = MASB(datadict, max_r=buf, denoise=None, detect_planar=None)

	# compute normals
	t1 = time()
	P = pcl.PointCloud(datadict['coords'])
	normals = P.calc_normals(k)
	t2 = time()
	print "finished normal computation in {} s".format(t2-t1)
	
	datadict['normals'] = np.array(normals, dtype=np.float32)

	io_npy.write_npy(npy_file_path, datadict)

	# compute ma
	ma.compute_balls()

	io_npy.write_npy(npy_file_path, datadict)

	del datadict
	del ma