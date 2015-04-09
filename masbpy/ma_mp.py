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

from numpy.random import rand
from numpy import array, zeros, concatenate, nan
import numpy as np
from itertools import chain

from pykdtree.kdtree import KDTree

from multiprocessing import Process, Pool, cpu_count, Manager
from multiprocessing.queues import Queue

try: 
    import numba
    from algebra import norm, dot, equal, compute_radius, cos_angle
except:
    from algebra import norm, dot, equal, compute_radius, cos_angle

import math

from time import time

class MASB(object):

    def __init__(self, datadict, max_r, denoise=None, denoise_delta=None, detect_planar=None):

        self.manager = Manager()
        self.D = datadict # dict of numpy arrays
        self.m, self.n = datadict['coords'].shape

        self.coords_with_buffer = concatenate([self.D['coords'], self.D['coords_in_buffer']])
        if datadict.has_key('coords_in_buffer'):
            self.kd_tree = KDTree(self.coords_with_buffer)
        else:
            self.kd_tree = KDTree(self.D['coords'])

        self.SuperR = max_r
        self.denoise = denoise
        self.denoise_delta = denoise_delta
        self.detect_planar = detect_planar
    
    def compute_sp(self):
        from Queue import Queue
        queue = Queue()
        datalen = len(self.D['coords'])
        self(queue,0,datalen, True, False)
        self(queue,0,datalen, False, False)
        return queue.get() + queue.get()

    def compute_balls(self, num_processes=cpu_count()):
        datalen = len(self.D['coords'])
        
        n = num_processes/2 # we are spawning 2 processes (inner and outer ma) per n
        batchsize = datalen/n
        chunk_bounds = []
        end=0
        for i in xrange(n-1):
            start = end
            end = (i+1)* batchsize -1
            chunk_bounds.append( (start, end) )
        start, end = end, datalen
        chunk_bounds.append((start, end))

        print "chunking at:", chunk_bounds

        jobs = []
        queue = self.manager.Queue()

        t1 = time()
        for s,e in chunk_bounds:
            p1 = Process(target=self, args=(queue,s,e, True, False))
            p1.start()
            jobs.append(p1)

            p2 = Process(target=self, args=(queue,s,e, False, False))
            p2.start()
            jobs.append(p2)
        
        result = []
        for j in jobs:
            j.join()
            res = queue.get()
            result.append(res)

        t2 = time()

        print "Finished ma computation in {} s".format(t2-t1)

        result.sort(key=lambda item: (item[1], item[0]))

        self.D['ma_coords_out'] = concatenate([ma_coords for start, inner, ma_coords, ma_f2 in result[:n] ])
        # self.D['ma_radii_out'] = concatenate([ma_radii for start, inner, ma_coords, ma_radii, ma_f2, shrinkhist in result[:n] ])
        self.D['ma_f2_out'] = concatenate([ma_f2 for start, inner, ma_coords, ma_f2 in result[:n] ])
        # self.D['ma_shrinkhist_out'] = list(chain(*[shrinkhist for start, inner, ma_coords, ma_radii, ma_f2, shrinkhist in result[:n] ]))
        
        self.D['ma_coords_in'] = concatenate([ma_coords for start, inner, ma_coords, ma_f2 in result[n:] ])
        # self.D['ma_radii_in'] = concatenate([ma_radii for start, inner, ma_coords, ma_radii, ma_f2, shrinkhist in result[n:] ])
        self.D['ma_f2_in'] = concatenate([ma_f2 for start, inner, ma_coords, ma_f2 in result[n:] ])
        # self.D['ma_shrinkhist_in'] = list(chain(*[shrinkhist for start, inner, ma_coords, ma_radii, ma_f2, shrinkhist in result[n:] ]))
        
        print "Finished datamerging in {} s".format(time()-t2)

    # @autojit
    # @profile
    def __call__(self, queue, start, end, inner=True, verbose=False):
        """Balls shrinking algorithm. Set `inner` to False when outer balls are wanted."""
        print 'processing', start, end, "inner:", inner#, hex(id(self.kd_tree)), hex(id(self.D))
        m = end-start
        ma_coords = zeros((m, self.n), dtype=np.float32)
        ma_coords[:] = nan
        # ma_radii = zeros(m)
        # ma_radii[:] = nan
        ma_f2 = zeros(m, dtype=np.uint32)
        ma_f2[:] = nan
        if self.denoise != None:
            self.denoise = (math.pi/180)*self.denoise
        if self.denoise_delta != None:
            self.denoise_delta = (math.pi/180)*self.denoise_delta
        if self.detect_planar != None:
            self.detect_planar = (math.pi/180)*self.detect_planar
        # q_history_list = []
        ZeroDivisionError_cnt = 0
        for i, pi in enumerate(xrange(start,end)):
            p, n = self.D['coords'][pi], self.D['normals'][pi]
            # print "for", p, n

            if np.isnan(n[0]):
                continue
            if not inner:
                n = -n
                        
            # use the previous point as initial estimate for q
            q=p
            # but, when approximating 1st point initialize q with random point not equal to p
            # if i==0:
            #     while equal(q,p):
            #         random_index = int(rand(1)*self.D['coords'].shape[0])
            #         q = self.D['coords'][random_index]
            #     r = compute_radius(p,n,q)
            # forget optimization of r:
            r=self.SuperR
            
            if verbose: print 'initial r: ' + str(r)

            r_ = None
            c = None
            j = -1
            q_i = None
            q_history = []
            while True:
                j+=1
                # initialize r on last found radius
                if j>0:
                    r = r_
                elif j==0 and i>0:
                    r = r

                # compute ball center
                c = p - n*r

                q_i_previous = q_i

                # find closest point to c and assign to q
                dists, results = self.kd_tree.query(array([c]), k=2)
                try:
                    candidate_c = self.coords_with_buffer[results]
                except IndexError:
                    import ipdb; ipdb.set_trace()
                q = candidate_c[0][0]
                q_i = results[0][0]

                # if i==64849:
                #     import ipdb; ipdb.set_trace()

                # What to do if closest point is p itself?
                # import ipdb; ipdb.set_trace()
                if equal(q,p):
                    # 1) if r==SuperR, apparantly no other points on the halfspace spanned by -n => that's an infinite ball
                    if r == self.SuperR: break
                    elif equal(candidate_c[0][0], candidate_c[0][1]): break
                    # 2) otherwise just pick the second closest point
                    else: 
                        q = candidate_c[0][1]
                        q_i = results[0][1]
                
                # q_history.append(q_i)
                # compute new candidate radius r_
                try:
                    r_ = compute_radius(p,n,q)
                except ZeroDivisionError:
                    ZeroDivisionError_cnt += 1
                    r_ = self.SuperR+1

                # if r_ < 0 closest point was on the wrong side of plane with normal n => start over with SuperRadius on the right side of that plance
                if r_ < 0.: r_ = self.SuperR
                # if r_ > SuperR, stop now because otherwise in case of planar surface point configuration, we end up in an infinite loop
                elif r_ > self.SuperR:
                    r_ = self.SuperR
                    break
                if verbose: print 'current ball: ' + str(i) +' - ' + str(r_)

                c_ = p - n*r_
                # import ipdb; ipdb.set_trace()
                if self.denoise != None:
                    try: 
                        if math.acos(cos_angle(p-c, q-c)) < self.denoise and j>0 and r_>norm(q-p):
                            r_=r
                            break
                    except ValueError:
                        import ipdb; ipdb.set_trace()

                if self.denoise_delta != None and j>0:
                    theta_now = math.acos(cos_angle(p-c_, q-c_))
                    q_previous = self.D['coords'][q_i_previous]
                    theta_prev = math.acos(cos_angle(p-c_, q_previous-c_))
                    
                    if theta_prev-theta_now > self.denoise_delta and r_>norm(q-p):
                        # keep previous radius:
                        r_=r
                        q_i = q_i_previous
                        break

                if self.detect_planar != None:
                    if math.acos( cos_angle(q-p, -n) ) > self.detect_planar:
                        r_= self.SuperR
                        break

                # stop iteration if r has converged
                if abs(r - r_) < 0.01:
                    break

                # stop iteration if this looks like an infinite loop:
                if j > 30:
                    if verbose: print "breaking possible infinite loop at j=30"
                    break

            if r_ >= self.SuperR or r_ == None:
                pass
            else:
                # ma_radii[i] = r_
                ma_coords[i] = c
                ma_f2[i] = q_i
            # q_history_list.append(q_history[:-1])

        result = ( start, inner, ma_coords, ma_f2 )
        queue.put( result )

        print '{} ZeroDivisionErrors'.format(ZeroDivisionError_cnt)
        print "done!", start, inner, "len:", ma_coords.shape