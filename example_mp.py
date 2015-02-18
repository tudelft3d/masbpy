from masbpy.ma_mp import MASB
from masbpy import io_ply
from masbpy.write import write_coords_filtered, write_coords_lfs_colored, write_ma_coords


if __name__ == '__main__':
    # read points and normals from a ply file
    datadict = io_ply.read_ply('example-data/house_dyke_tree.ply')
    
    # compute interior and exterior MAT
    ma = MASB(datadict, 10)
    ma.compute_mp()
    # write MA points to file
    write_ma_coords(datadict)