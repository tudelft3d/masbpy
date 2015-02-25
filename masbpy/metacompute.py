import numpy as np
from algebra_numba import norm, dot, equal, proj, compute_radius, cos_angle


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
