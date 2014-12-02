from masbpy import MASB, read_ply
from masbpy.write import write_coords_filtered, write_coords_lfs_colored, write_ma_coords


if __name__ == '__main__':
    # read points and normals from a ply file
    datadict = read_ply('example-data/house_dyke_tree.ply')
    
    # compute interior and exterior MAT
    ma = MASB(datadict, 10)
    ma.compute_balls(inner=True)
    ma.compute_balls(inner=False)
    # write MA points to file
    write_ma_coords(datadict)

    # compute Local Feature Size and write result to file for visuatization
    ma.compute_lfs()
    write_coords_lfs_colored(datadict)

    # perform thinning and write result to file
    ma.decimate_lfs(epsilon=0.4)
    write_coords_filtered(datadict, filter_key='decimate_lfs')