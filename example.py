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

from masbpy.ma import MASB
# or for multiprocessing:
# from masbpy.ma_mp import MASB

from masbpy import io_npy, io_ply

def main():
    # read points and normals from a ply file
    datadict = io_ply.read_ply('example-data/house_dyke_tree.ply')
    
    # compute interior and exterior MAT
    ma = MASB(datadict, 10)
    ma.compute_balls()

    # write MA points to file
    io_npy.write_npy('house_dyke_tree_npy', datadict)

if __name__ == '__main__':
    main()