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

import math
from numba import jit

# numba based operations for 3D vectors only

@jit
def norm(vec):
    """ Calculate the norm of a 3d vector. """
    return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

@jit
def dot(vec1, vec2):
    """ Calculate the dot product of two 3d vectors. """
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

@jit
def equal(vec1, vec2):
    return vec1[0]==vec2[0] and vec1[1]==vec2[1] and vec1[2]==vec2[2]

@jit
def normalize(vec):
    """ Calculate the normalized vector (norm: one). """
    return vec / norm(vec)

# @jit
# def cross(vec1, vec2):
#     """ Calculate the cross product of two 3d vectors. """
#     a1, a2, a3 = double(vec1[0]), double(vec1[1]), double(vec1[2])
#     b1, b2, b3 = double(vec2[0]), double(vec2[1]), double(vec2[2])
#     result = np.zeros(3)
#     result[0] = a2 * b3 - a3 * b2
#     result[1] = a3 * b1 - a1 * b3
#     result[2] = a1 * b2 - a2 * b1
#     return result

@jit
def proj(u,v):
	factor = dot(u,v) / dot(u,u)
	return [factor*u[0], factor*u[1], factor*u[2]]

@jit
def cos_angle(p,q):
    """Calculate the cosine of angle between vector p and q
    see http://en.wikipedia.org/wiki/Law_of_cosines#Vector_formulation
    """
    cos_angle = dot(p,q) / ( norm(p) * norm(q) )
    if cos_angle > 1: return 1
    elif cos_angle < -1: return -1
    else: return cos_angle

@jit
def compute_radius(p, p_n, q):
    """compute radius of ball that touches points p and q and is centered on along the normal p_n of p. Numpy array inputs."""
    # this is basic goniometry
    d = norm(p-q)
    cos_theta = dot(p_n,p-q) / d
    return d/(2*cos_theta)