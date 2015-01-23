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

import sys, argparse
from masbpy.ma_fast import MASB
from masbpy import io_ply, io_npy

def compute_lfs(datadict, k=10):
    import numpy as np
    from pykdtree.kdtree import KDTree

    # collect all ma_coords that are not NaN
    ma_coords = np.concatenate([datadict['ma_coords_in'], datadict['ma_coords_out']])
    ma_coords = ma_coords[~np.isnan(ma_coords).any(axis=1)]

    # build kd-tree of ma_coords to compute lfs
    pykdtree = KDTree(ma_coords)
    if k > 1:
        datadict['lfs'] = np.sqrt(np.median(pykdtree.query(datadict['coords'], k)[0], axis=1))
    else:
        datadict['lfs'] = np.sqrt(pykdtree.query(datadict['coords'], k)[0])

def main(args):
    if args.infile.endswith('ply'):
        datadict = io_ply.read_ply(args.infile)
    elif args.infile.endswith('npy'):
        datadict = io_npy.read_npy(args.infile, ['coords', 'normals'])
    
    # compute interior and exterior MAT
    ma = MASB(datadict, args.radius, denoise=args.denoise, detect_planar=args.planar)
    ma.compute_mp()

    if args.lfs:
        compute_lfs(datadict)

    io_npy.write_npy(args.outfile, datadict)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Compute MAT and LFS')
    parser.add_argument('infile', help='Input .ply, _npy')
    parser.add_argument('outfile', help='Output _npy')
    parser.add_argument('--without_lfs', help='Don\'t compute LFS', dest='lfs', action='store_false')
    parser.set_defaults(lfs=False)
    parser.add_argument('-r', '--radius', help='initial ball radius', default=200, type=float)
    parser.add_argument('-d', '--denoise', help='denoising parameter', default=40, type=float)
    parser.add_argument('-p', '--planar', help='planarity parameter', default=75, type=float)

    args = parser.parse_args()
    main(args)