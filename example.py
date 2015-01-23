from masbpy.ma import MASB
# or for multiprocessing:
# from masbpy.ma_mp import MASB

from masbpy import io_npy, io_ply

def main():
    # read points and normals from a ply file
    datadict = io_ply.read_ply('example-data/house_dyke_tree.ply')
    
    # compute interior and exterior MAT
    ma = MASB(datadict, 10)
    ma.compute_balls

    # write MA points to file
    io_npy.write_npy('house_dyke_tree_npy', datadict)

if __name__ == '__main__':
    main()