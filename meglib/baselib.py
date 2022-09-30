'''
Basic utility functions.  Written by Michael Glinsky.
'''
import numpy as np
from scipy import linalg
import os.path
import pickle
import zipfile
from copy import deepcopy

class AttrDict(dict):
    '''
    class to set up an attribute dictionary.  Useful in setting up  and referencing
    a group of parameters.
    ``my_attrdict.__class__.__name__ = 'AttrDict'``;  after read with old class
    '''
    def __getattr__(self, k): return self[k]
    def __setattr__(self, k, v): self[k] = v
    
def append_list(base_list, add_list, name_list):
    '''
    adds each element in *add_list* to *base_list* after appending '_' + *name_list*
    '''
    for name in add_list:
        base_list.append(name + '_' + name_list)
        
def read_pickled_object(filename, file_extension):
    '''
    read a object from a zipped Pickle file of the object. *filename* is the root
    filename that will be read which will have *file_extension* added to it.
    '''
    (path, name) = os.path.split(filename)
    cwd = os.getcwd()
    if path == '':
        pass
    else:
        os.chdir(path)
    
    with zipfile.ZipFile(name + "." + file_extension, 'r') as myzip:
        myzip.extractall()
    
    with open("obj.tmp.pickle", "rb") as f:
        obj = pickle.load(f)
            
    os.remove("obj.tmp.pickle")
    os.chdir(cwd)
    
    return obj
    
def write_pickled_object(obj, filename, file_extension):
    '''
    write an *obj* to a zipped Pickle file with *filename* and *file_extension*
    '''
    (path, name) = os.path.split(filename)
    cwd = os.getcwd()
    if path == '':
        pass
    else:
        os.chdir(path)
        
    with open("obj.tmp.pickle", "wb") as f:
        pickle.dump(obj, f)
        
    with zipfile.ZipFile(name + "." + file_extension, 'w', zipfile.ZIP_DEFLATED) as myzip:
        myzip.write("obj.tmp.pickle")
        
    os.remove("obj.tmp.pickle")
    os.chdir(cwd)
    
def save_figs(path='', name=''):
    '''
    save all open figures to *path* + *name* _fig_i.png
    '''
    import matplotlib.pyplot as plt
    from os.path import join, expanduser
    
    for i in plt.get_fignums():
        plt.figure(i)
       	if name == '':
       	    file_root = 'fig'
       	else:
       	    file_root = name + '_fig'
       	plt.savefig(expanduser(join(path, file_root + '_%d.png' % i)))
   	
def test_path(fname, test_directory='~/code/pysnl/run_parameters'):
    '''
    form expanded path for *test_directory* / *fname*
    '''
    import os
    return os.path.expanduser(os.path.join(test_directory, fname))
    
#################################################################################################
class CoordinateTransform:
    '''
    data model for a coordinate transform between ``(i,j)`` and ``(x,y)``
    '''
    def __init__(self):
        self.A = np.identity(2)
        self.b = np.zeros(2)
        self.A_inv = linalg.inv(self.A)
        self.b_inv = - self.A_inv.dot(self.b)
        self.utm = ""
        
    def my_str(self, space=''):
        string = ""
        string += space + "A =" + "\n"
        string += space + str(self.A) + "\n"
        string += space + "b =" + "\n"
        string += space + str(self.b) + "\n"
        return string
        
    def __str__(self):
        return self.my_str()
        
    def __eq__(self, other):
        if (self.A == other.A).all() and (self.b == other.b).all():
            return True
        else:
            return False
        
    def three_point_set(self, x_y_points, i_j_points, utm = ""):
        '''
        sets the coordinate transformation given three points in each coordinate system.
        *x_y_points* is a list of the three points in ``(x,y)`` space. *i_j_points* are
        a list of the three points in ``(ep,cdp)`` space.
        '''
        self.utm = utm
        
        dx = np.array([np.array(x_y_points[2]) - np.array(x_y_points[0]), np.array(x_y_points[1]) - np.array(x_y_points[0])])
        ds = np.array([np.array(i_j_points[2]) - np.array(i_j_points[0]), np.array(i_j_points[1]) - np.array(i_j_points[0])])
        
        dx = dx.T
        ds = ds.T
        
        self.A = dx.dot(linalg.inv(ds))
        self.b = x_y_points[0] - self.A.dot(ep_cdp_points[0])
        self.A_inv = linalg.inv(self.A)
        self.b_inv = - self.A_inv.dot(self.b)
        
    def x_y(self, i_j):
        '''
        returns an ``(x,y)`` point given a ``(i,j)`` point
        '''
        return self.A.dot(i_j) + self.b
        
    def i_j(self, x_y):
        '''
        returns a ``(i,j)`` point given an ``(x,y)`` point
        '''
        return self.A_inv.dot(x_y) + self.b_inv
        
    def x_y_T(self, ep_cdp):
        '''
        returns an ``(x,y)`` point given a ``(i,j)`` point
        '''
        return np.array(ep_cdp).dot(self.A.T) + self.b
        
    def i_j_T(self, x_y):
        '''
        returns a ``(i,j)`` point given an ``(x,y)`` point
        '''
        return np.array(x_y).dot(self.A_inv.T) + self.b_inv
        
    def x_y_array(self, i, j):
        '''
        returns arrays of the x and y coordinates given arrays of the ep and
        cdp coordinates
        '''
        s = np.array([i,j])
        x = (s.T.dot(self.A.T) + self.b).T
        return x[0,:,:], x[1,:,:]
        
    def i_j_array(self, x_in, y_in):
        '''
        returns arrays of the ep and cdp coordinates given arrays of the x and
        y coordinates
        '''
        x = np.array([x_in,y_in])
        s = (x.T.dot(self.A_inv.T) + self.b_inv).T
        return s[0,:,:], s[1,:,:]
        
    def x_y_vector(self, ep, cdp):
        '''
        returns vectors of the x and y coordinates given vectors of the ep and
        cdp coordinates
        '''
        s = np.array([ep,cdp])
        x = (s.T.dot(self.A.T) + self.b).T
        return x[0,:], x[1,:]
        
    def i_j_vector(self, x_in, y_in):
        '''
        returns vectors of the i and j coordinates given vectors of the x and
        y coordinates
        '''
        x = np.array([x_in,y_in])
        s = (x.T.dot(self.A_inv.T) + self.b_inv).T
        return s[0,:], s[1,:]
        
    def clone(self):
        new_transform = CoordinateTransform()
        
        new_transform.A = deepcopy(self.A)
        new_transform.b = deepcopy(self.b)
        new_transform.A_inv = deepcopy(self.A_inv)
        new_transform.b_inv = deepcopy(self.b_inv)
        
        return new_transform
            
    def copy_obj(self, old_transform):
        self.A = deepcopy(old_transform.A)
        self.b = deepcopy(old_transform.b)
        self.A_inv = deepcopy(old_transform.A_inv)
        self.b_inv = deepcopy(old_transform.b_inv)
        
        return self
            
