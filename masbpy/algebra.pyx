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

from __future__ import division
cimport cython


import numpy as np
cimport numpy as np
# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.float32
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.float32_t DTYPE_t

from libc.math cimport sqrt

# cythonized operations for 3D vectors only

@cython.boundscheck(False)
cpdef norm(np.ndarray[DTYPE_t, ndim=1] vec):
    """ Calculate the norm of a 3d vector. """
    return sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

@cython.boundscheck(False)
cpdef dot(np.ndarray[DTYPE_t, ndim=1] vec1, np.ndarray[DTYPE_t, ndim=1] vec2):
    """ Calculate the dot product of two 3d vectors. """
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

@cython.boundscheck(False)
cpdef equal(np.ndarray[DTYPE_t, ndim=1] vec1, np.ndarray[DTYPE_t, ndim=1] vec2):
    return vec1[0]==vec2[0] and vec1[1]==vec2[1] and vec1[2]==vec2[2]

@cython.boundscheck(False)
cpdef normalize(vec):
    """ Calculate the normalized vector (norm: one). """
    return vec / norm(vec)

@cython.boundscheck(False)
cpdef proj(np.ndarray[DTYPE_t, ndim=1] u, np.ndarray[DTYPE_t, ndim=1] v):
    cdef double factor = dot(u,v) / dot(u,u)
    return [factor*u[0], factor*u[1], factor*u[2]]

@cython.boundscheck(False)
cpdef cos_angle(np.ndarray[DTYPE_t, ndim=1] p, np.ndarray[DTYPE_t, ndim=1] q):
    """Calculate the cosine of angle between vector p and q
    see http://en.wikipedia.org/wiki/Law_of_cosines#Vector_formulation
    """
    cdef double cos_angle = dot(p,q) / ( norm(p) * norm(q) )
    if cos_angle > 1: return 1
    elif cos_angle < -1: return -1
    else: return cos_angle

@cython.boundscheck(False)
cpdef compute_radius(np.ndarray[DTYPE_t, ndim=1] p, np.ndarray[DTYPE_t, ndim=1] p_n, np.ndarray[DTYPE_t, ndim=1] q):
    """compute radius of ball that touches points p and q and is centered on along the normal p_n of p. Numpy array inputs."""
    # this is basic goniometry
    cdef double d = norm(p-q)
    cdef double cos_theta = dot(p_n,p-q) / d
    return d/(2*cos_theta)