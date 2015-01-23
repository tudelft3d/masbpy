from sklearn.decomposition import PCA
from pykdtree.kdtree import KDTree
from multiprocessing import Pool
from time import time
from masbpy import io_npy
import numpy as np
import sys
import argparse


def compute_normal(neighbours):
	pca = PCA(n_components=3)
	pca.fit(neighbours)
	plane_normal = pca.components_[-1] # this is a normalized normal
	# make all normals point upwards:
	if plane_normal[-1] < 0:
		plane_normal *= -1
	return plane_normal

def main(args):
	if args.infile.endswith('ply'):
		from masbpy import io_ply
		datadict = io_ply.read_ply(args.infile)
	elif args.infile.endswith('las'):
		from masbpy import io_las
		datadict = io_las.read_las(args.infile)
	elif args.infile.endswith('npy'):
		datadict = io_npy.read_npy(args.infile, ['coords'])
	
	kd_tree = KDTree( datadict['coords'] )
	neighbours = kd_tree.query( datadict['coords'], args.k+1 )[1]
	neighbours = datadict['coords'][neighbours]
	
	p = Pool()
	t1 = time()
	normals = p.map(compute_normal, neighbours)
	t2 = time()
	print "finished normal computation in {} s".format(t2-t1)
	
	datadict['normals'] = np.array(normals, dtype=np.float32)

	io_npy.write_npy(args.outfile, datadict)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Basic PCA normal approximation')
    parser.add_argument('infile', help='Input .las, .ply, _npy')
    parser.add_argument('outfile', help='Output _npy')
    parser.add_argument('-k', help='Number of neighbours to use', default=10, type=int)

    args = parser.parse_args()
    main(args)