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

from multiprocessing import Pool
import numpy as np
try: 
    import numba
    from algebra_numba import norm, dot, equal, compute_radius, cos_angle
except:
    from algebra import norm, dot, equal, compute_radius, cos_angle


def compute_surface_variation(datadict, k=10):
    from pykdtree.kdtree import KDTree
    from sklearn.decomposition import PCA

    def f(neighbours):
        pca = PCA(n_components=3)
        pca.fit(neighbours)
        return pca.components_[-1]/(pca.components_[0]+pca.components_[1]+pca.components_[2]) # this is a normalized normal
    

    pykdtree = KDTree(coords)
    neighbours = kd_tree.query( datadict['coords'], k+1 )[1]
    neighbours = datadict['coords'][neighbours]
    
    p = Pool()
    result = p.map(f, neighbours)
    D['surfvar'] = np.array(result, dtype=np.float32)


def compute_lfs(datadict, k=10):
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

def compute_lam(D, inner='in'):
    '''Compute for every boundary point p, corresponding ma point m, and other feature point p_ the distance p-p_ '''
    D['lam_'+inner] = np.zeros(D['coords'].shape[0])
    D['lam_'+inner][:] = np.nan

    for i, p in enumerate(D['coords']):
        c_p = D['ma_coords_'+inner][i]
        if not np.isnan(c_p[0]):
            p_ = D['coords'][D['ma_f2_'+inner][i]]
            D['lam_'+inner][i] = norm(p-p_)

def compute_theta(D, inner='in'):
    '''Compute for every boundary point p, corresponding ma point m, and other feature point p_ the angle p-m-p_ '''
    D['theta_'+inner] = np.zeros(D['coords'].shape[0])
    D['theta_'+inner][:] = np.nan

    for i, p in enumerate(D['coords']):
        c_p = D['ma_coords_'+inner][i]
        if not np.isnan(c_p[0]):
            p_ = D['coords'][D['ma_f2_'+inner][i]]
            D['theta_'+inner][i] = cos_angle(p-c_p, p_-c_p)
