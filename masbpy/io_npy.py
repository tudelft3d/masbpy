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

import os
import numpy as np

def write_npy(dir, datadict, keys=[]):
	if not os.path.exists(dir):
	    os.makedirs(dir)

	for key,val in datadict.items():
		if key in keys or len(keys)==0:
			fname = os.path.join(dir,key)
			np.save(fname, val)

def read_npy(dir, keys=[]):
	assert os.path.exists(dir)

	if len(keys)==0:
		keys = inspect_npy(dir)

	datadict = {}	
	for key in keys:
		fname = os.path.join(dir,key+'.npy')
		if os.path.exists(fname):
			datadict[key] = np.load(fname)
	return datadict

def inspect_npy(dir):
	from glob import glob
	dir = os.path.join(dir,'*')
	return [os.path.split(f)[-1].split('.')[0] for f in glob(dir)]