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

import sys, argparse
from masbpy.ma_mp import MASB
from masbpy import io_ply, io_npy, metacompute


def main(args):
    if args.infile.endswith('ply'):
        datadict = io_ply.read_ply(args.infile)
    elif args.infile.endswith('npy'):
        if args.ma:
            datadict = io_npy.read_npy(args.infile, ['coords', 'normals'])
        else:
            datadict = io_npy.read_npy(args.infile, ['coords', 'ma_coords_in', 'ma_coords_out'])
    
    # compute interior and exterior MAT
    if args.ma:
        ma = MASB(datadict, args.radius, denoise=args.denoise, detect_planar=args.planar)
        ma.compute_balls()

    if args.lfs or not args.ma:
        metacompute.compute_lfs(datadict)

    io_npy.write_npy(args.outfile, datadict)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Compute MAT and LFS')
    parser.add_argument('infile', help='Input .ply, _npy')
    parser.add_argument('outfile', help='Output _npy')
    parser.add_argument('--noma', help='Don\'t compute MAT', dest='ma', action='store_false')
    parser.set_defaults(ma=True)
    parser.add_argument('--with-lfs', help='Also compute LFS', dest='lfs', action='store_true')
    parser.set_defaults(lfs=False)
    parser.add_argument('-r', '--radius', help='initial ball radius', default=200, type=float)
    parser.add_argument('-d', '--denoise', help='denoising parameter', default=20, type=float)
    parser.add_argument('-p', '--planar', help='planarity parameter', default=75, type=float)

    args = parser.parse_args()
    main(args)
