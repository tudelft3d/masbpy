import glob
from multiprocessing import Pool
from time import time
from datetime import datetime
import logging

import laspy
import numpy as np
from masbpy.ma_mp import MASB
from masbpy import io_npy, metacompute

from sklearn.decomposition import PCA

# las_tiles = glob.glob('/Volumes/HFS2000/*.las')
las_tiles = glob.glob('/Volumes/HFS2000/CA_pressure_ridge/CA_pressure_ridge_tile_*.las')
mode = ''

tile_size = 750
buf = 100
k = 10
skip_some_tiles = 0

logging.basicConfig(filename='./tiling_ma_CA.log',level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s')


def compute_normal(neighbours):
	pca = PCA(n_components=3)
	pca.fit(neighbours)
	plane_normal = pca.components_[-1] # this is a normalized normal
	# make all normals point upwards:
	if plane_normal[-1] < 0:
		plane_normal *= -1
	return plane_normal

for las_file_path in las_tiles[skip_some_tiles:]:
	t_start = time()
	npy_file_path = las_file_path[:-4]+mode+'_npy'
	logging.info('{} Starting with file {}'.format(datetime.now().isoformat(), npy_file_path))

	las_file = laspy.file.File(las_file_path)

	
	# get bounding box without buffer
	bb_min = las_file.header.get_min()
	bb_max = las_file.header.get_max()
	bb_min[0] += buf
	bb_min[1] += buf
	bb_max[0] -= buf
	bb_max[1] -= buf
	center_x = (bb_max[0] - bb_min[0])/2
	center_y = (bb_max[1] - bb_min[1])/2

	# seperate points inside and outside bufferless bounding box
	x_inside_mask = np.logical_and(np.greater(las_file.x, bb_min[0]), np.less(las_file.x, bb_max[0]))
	y_inside_mask = np.logical_and(np.greater(las_file.y, bb_min[1]), np.less(las_file.y, bb_max[1]))
	inside_mask = np.logical_and(x_inside_mask, y_inside_mask)
	coord_inside_count = inside_mask.sum()
	
	if coord_inside_count == 0:
		logging.warning("skipping {}, too few points".format(las_file_path))
		continue
	
	datadict = {}
	datadict['coords'] = np.concatenate([ 
		np.column_stack([ np.array(a[inside_mask], dtype=np.float32) for a in [las_file.x-center_x, las_file.y-center_y, las_file.z] ]),
		np.column_stack([ np.array(a[~inside_mask], dtype=np.float32) for a in [las_file.x-center_x, las_file.y-center_y, las_file.z] ])
		])

	del inside_mask, x_inside_mask, y_inside_mask
	las_file.close()

	# import ipdb; ipdb.set_trace()
	# creat MASB object, so that also KDtree gets created
	ma = MASB(datadict, max_r=buf, denoise=35, detect_planar=65, coord_inside_count=coord_inside_count)

	# compute normals
	neighbours = ma.kd_tree.query( datadict['coords'][:coord_inside_count,:], k+1 )[1]
	neighbours = datadict['coords'][neighbours]
	
	p = Pool()
	t_start_normals = time()
	normals = p.map(compute_normal, neighbours)
	p.close()
	p.join()
	t_stop_normals = time()
	logging.info("finished normal computation in {} s".format(t_stop_normals-t_start_normals))
	
	datadict['normals'] = np.array(normals, dtype=np.float32)

	io_npy.write_npy(npy_file_path, datadict)

	# compute ma
	t_start_ma = time()
	ma.compute_balls()
	t_stop_ma = time()
	logging.info("finished MAT computation in {} s".format(t_stop_ma-t_start_ma))
	datadict['coords'] = datadict['coords'][:coord_inside_count,:]
	datadict['coords'] += np.array([center_x, center_y, 0])
	datadict['ma_coords_in'] += np.array([center_x, center_y, 0])
	datadict['ma_coords_out'] += np.array([center_x, center_y, 0])

	io_npy.write_npy(npy_file_path, datadict)

	# t_start_lfs = time()
	# metacompute.compute_lfs(datadict)
	# t_stop_lfs = time()
	# logging.info("finished LFS computation in {} s".format(t_stop_lfs-t_start_lfs))

	del datadict
	del ma
	del normals
	t_stop = time()

	logging.info('Finished all computations')
	logging.info('number of points %d', coord_inside_count)
	logging.info('total time {}'.format(t_stop-t_start))