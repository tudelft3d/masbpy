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

# Copyright 2015 Ravi Peters

#!/usr/bin/env python

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
	p.close()
	
	datadict['normals'] = np.array(normals, dtype=np.float32)

	io_npy.write_npy(args.outfile, datadict)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Basic PCA normal approximation')
    parser.add_argument('infile', help='Input .las, .ply, _npy')
    parser.add_argument('outfile', help='Output _npy')
    parser.add_argument('-k', help='Number of neighbours to use', default=10, type=int)

    args = parser.parse_args()
    main(args)