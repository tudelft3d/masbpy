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
import numpy as np
from pykdtree.kdtree import KDTree

# with numba we get significant speedups
try: 
    import numba
    from algebra_numba import norm, dot, equal, compute_radius, cos_angle
except:
    from algebra import norm, dot, equal, compute_radius, cos_angle

# FIXME: can't handle duplicate points in input

class MASB(object):

    def __init__(self, datadict, max_r, denoise_absmin=None, denoise_delta=None, denoise_min=None, detect_planar=None):
        self.D = datadict # dict of numpy arrays

        self.pykdtree = KDTree(self.D['coords'])

        self.m, self.n = datadict['coords'].shape
        self.D['ma_coords_in'] = np.empty( (self.m,self.n), dtype=np.float32 )
        self.D['ma_coords_in'][:] = np.nan
        self.D['ma_coords_out'] = np.empty( (self.m,self.n), dtype=np.float32 )
        self.D['ma_coords_out'][:] = np.nan
        self.D['ma_q_in'] = np.zeros( (self.m), dtype=np.uint32 )
        self.D['ma_q_in'][:] = np.nan
        self.D['ma_q_out'] = np.zeros( (self.m), dtype=np.uint32 )
        self.D['ma_q_out'][:] = np.nan

        self.SuperR = max_r
        self.delta_convergence = 0.001
        self.iteration_limit = 30

        if denoise_absmin is None:
            self.denoise_absmin = None
        else:
            self.denoise_absmin = (math.pi/180)*denoise_absmin
        if denoise_delta is None:
            self.denoise_delta = None
        else:
            self.denoise_delta = (math.pi/180)*denoise_delta
        if denoise_min is None:
            self.denoise_min = None
        else:
            self.denoise_min = (math.pi/180)*denoise_min

        if detect_planar is None:
            self.detect_planar = None
        else:
            self.detect_planar = (math.pi/180)*detect_planar

    def compute_balls(self):
        for inner in [True, False]:
            self.compute_balls_oneside(inner)

    def compute_balls_oneside(self, inner=True):
        """Balls shrinking algorithm. Set `inner` to False when outer balls are wanted."""

        # iterate over all point-normal pairs
        for p_i in xrange(self.m):
            p, n = self.D['coords'][p_i], self.D['normals'][p_i]
            #-- p is the point along whose normal n we are shrinking a ball, its index is p_i
            
            if not inner:
                n = -n
            
            # initialize some helper variables:
            #-- q will represent the second point that defines a ball together with p and n
            q = None 
            #-- q_i is the index of q
            q_i = None
            #-- r represents the ball radius found in the current iteration (i.e. of the while loop below)
            r = None
            #-- r_previous represents the ball radius found in the previous iteration
            r_previous=self.SuperR
            #-- c is the ball's center point in the current iteration
            c = None
            #-- c_previous is the ball's center point in the previous iteration
            c_previous = None
            #-- j counts the iterations
            j = -1
            
            while True:
                # increment iteration counter
                j+=1
                # set r to last found radius if this isn't the first iteration
                if j>0:
                    r_previous = r

                # compute ball center
                c = p - n*r_previous
                
                # keep track of this for denoising purpose
                q_i_previous = q_i


                ### FINDING NEAREST NEIGHBOR OF c

                # find closest point to c and assign to q

                dists, indices = self.pykdtree.query(np.array([c]), k=2)

                try:
                    candidate_c = self.D['coords'][indices]
                except IndexError as detail:
                    print detail, indices, dists
                    import pdb; pdb.set_trace()
                    raise

                q = candidate_c[0][0]
                q_i = indices[0][0]
                
                # What to do if closest point is p itself?
                if equal(q,p):
                    # 1) if r_previous==SuperR, apparantly no other points on the halfspace spanned by -n => that's an infinite ball
                    if r_previous == self.SuperR: 
                        r = r_previous
                        break
                    # 2) otherwise just pick the second closest point
                    else: 
                        q = candidate_c[0][1]
                        q_i = indices[0][1]

                ### END FINDING NEAREST NEIGHBOR OF c
                # compute new candidate radius r
                try:
                    r = compute_radius(p,n,q)
                except ZeroDivisionError:
                    # this happens on some rare occasions, we'll just skip the point
                    # print 'ZeroDivisionError: excepting p: {} with n={} and q={}'.format(p,n,q)
                    break


                ### EXCEPTIONAL CASES

                # if r < 0 closest point was on the wrong side of plane with normal n => start over with SuperRadius on the right side of that plane
                if r < 0: 
                    r = self.SuperR
                # if r > SuperR, stop now because otherwise in case of planar surface point configuration, we end up in an infinite loop
                elif r > self.SuperR:
                    r = self.SuperR
                    break

                ### END EXCEPTIONAL CASES


                ### DENOISING STUFF
                # i.e. terminate iteration early if certain conditions are satisfied based on (history of) ball metrics

                c_ = p - n*r
                # this seems to work well against noisy ma points.
                if self.denoise_absmin is not None:
                    if math.acos(cos_angle(p-c_, q-c_)) < self.denoise_absmin and j>0 and r>norm(q-p):
                        # keep previous radius:
                        r=r_previous
                        q_i = q_i_previous
                        break

                if self.denoise_delta is not None and j>0:
                    theta_now = math.acos(cos_angle(p-c_, q-c_))
                    q_previous = self.D['coords'][q_i_previous]
                    theta_prev = math.acos(cos_angle(p-c_, q_previous-c_))
                    
                    if theta_prev-theta_now > self.denoise_delta and theta_now < self.denoise_min and r>norm(q-p):
                        # keep previous radius:
                        r=r_previous
                        q_i = q_i_previous
                        break

                if self.detect_planar != None:
                    if math.acos( cos_angle(q-p, -n) ) > self.detect_planar and j<2:
                        r= self.SuperR
                        break

                ### END DENOISING STUFF


                # stop iteration if r has converged
                if abs(r_previous - r) < self.delta_convergence:
                    break

                # stop iteration if this looks like an infinite loop:
                if j > self.iteration_limit:
                    # print "breaking for possible infinite loop"
                    break

            # now store valid points in array (invalid points will be NaN)
            if inner: inout = 'in'
            else: inout = 'out'
            
            if r >= self.SuperR:
                pass
            else:
                # self.D['ma_radii_'+inout][p_i] = r
                self.D['ma_coords_'+inout][p_i] = c
                self.D['ma_q_'+inout][p_i] = q_i
