from StringIO import StringIO
import numpy as np
import matplotlib.cm as cm

def write_coords_filtered(datadict, filter_key, name='coords_filtered'):
    with open(name+'.xyz', 'w') as f, open(name+'_c.xyz', 'w') as f_:
        m,n = datadict['coords'].shape
        for p, dec in zip(datadict['coords'], datadict[filter_key]):
            if not dec:
                f.write("{0} {1} {2}\n".format(p[0], p[1], p[2]))
            else:
                f_.write("{0} {1} {2}\n".format(p[0], p[1], p[2]))

def write_coords_lfs_colored(datadict, max_lfs=2, name='coords_lfs'):
    with open(name+'.off', 'w') as f:
        f.write("COFF\n")
        m,n = datadict['coords'].shape
        f.write("{} 0 0\n".format(m))

        for p, lfs in zip(datadict['coords'], datadict['lfs']):
            if not np.isnan(lfs):
                red=green=blue=0
                colorval = 255-int(255 * (lfs/max_lfs))
                if colorval > 255: colorval = 255
                if colorval < 0: colorval = 0
                rgba = cm.jet([colorval])[0]

                f.write("{0} {1} {2} {3} {4} {5} {6}\n".format(p[0], p[1], p[2], int(rgba[0]*255),int(rgba[1]*255),int(rgba[2]*255),int(rgba[3]*255)))

def write_ma_coords(datadict, name='ma_coords'):
    def write(ma_coords, filename, color):
        output = StringIO()

        point_count = 0

        for p in ma_coords:
            if not np.isnan(p[0]):
                red=green=blue=0

                colorval = 255                
                
                if color == 'red':
                    red=colorval
                elif color == 'blue':
                    blue=colorval
                elif color == 'orange':
                    blue=red = colorval
                else:
                    green=colorval

                print >>output, "{0} {1} {2} {3} {4} {5} 255".format(p[0], p[1], p[2], red,green,blue)
                point_count += 1

        with open(filename, 'w') as f:
            f.write("COFF\n")
            f.write("{} 0 0\n".format(point_count))
            f.write(output.getvalue())

    write(datadict['ma_coords_in'], name+'_inner.off', 'red')
    write(datadict['ma_coords_out'], name+'_outer.off', 'orange')