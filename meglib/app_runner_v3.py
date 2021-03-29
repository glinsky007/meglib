'''
AppRunner template class

General programming pattern for a technical application programmed in Python using a Traited
object.  An example of how to create your own extension of the object to make your own 
application is given in the **DemoApp** class.  The object has a save() and load() method to save and
load the state of the run of the job, an edit() method that presents a GUI editor for the parameters
of the application.  The job can be interactively executed from the GUI or from the command line.
Examples of how to execute and test the class are shown in the procedure test_app_runner().

The methods that need to be defined for a specific application are run() and plot().  If the output of
the application is only in memory, save_output() and load_output() methods to a format on disk should
also be defined.

The class also supports versions of the application in the *app_version* (Str) and *app_version_number* 
(CFloat) attributes.  The convert_parm() method will convert the parameters from one version to
another.

This programming pattern can also be used, with possibly some slight modification, for construction of data or
model objects.  For data objects, the attributes will store the meta information for the data object
and where the raw data can be stored.  Instead of run() and plot() methods, get_data() and set_data()
methods need to be defined.

Updated in March 2021 to run under Python v3

Copyright (c) 2018 Michael Glinsky, qiTech Consulting
for licence (MIT) see LICENSE.txt
'''

import os, sys, errno
from os.path import expanduser, join
import shutil
import time
import inspect
import numpy as np
import matplotlib.pyplot as plt

from traits.api import HasTraits, CFloat, CInt, Property, Range, Instance, Enum
from traits.api import Str, Array, List, Button, File, Directory, Dict, Bool

class AppRunner(HasTraits):
    '''
    Class to run the application
    '''
    
    # declare Traited attributes
    output_variables = List(Str, label='output variable lists', help='hidden, list of variables to save and load')
    print_variables = List(Str, label='output variable lists', help='hidden, list of variables to save and load')
    edit_exclude_variables = List(Str, label='edit exclude variables', help='hidden, variables to exclude from restricted editor')
    parm_file = File(join('~','parm.npz'), label='parameter file name', help='name of file to load and save parmeters to/from')
    app_type = Str('AppRunner', label='application', help='hidden, type of application')
    app_version = Str('0_1', label='version', help='hidden, application version as string')
    app_version_number = CFloat(0.1, label='version number', help='hidden, application version as number')
    run_name = Property(depends_on=['parm_file'], label='base run name')
    tmp_directory = Directory(join('~','tmp'), label='temporary directory', help='directory to hold temparary files')
    input_directory = Directory(join('~','data'), label='input directory', help='directory that hold input files')
    output_directory = Directory(join('~','tmp','output_directory'), label='output directory', help='directory to hold output files')
    description = Str('This is what Run #1 does', label='description of run')
                
    def app_type_version(self):
        '''
        Returns the name of the application and version number
        ##### need to be replaced with app specific code #####
        '''
        return 'AppRunner', '0_01', 0.01
        
    def __init__(self, parm_file=None, **p):
        self.app_type, self.app_version, self.app_version_number = self.app_type_version()
        if not not parm_file:
            self.parm_file = parm_file
            self.load()
        for name in p:
            setattr(self, name, p[name])
    
    def __str__(self, space=''):
        if not self.print_variables:
            print_variables = self.default_print_variables()
        else:
            print_variables = self.print_variables
        
        string = '\n' + space + self.app_type + ' (v' + self.app_version + '):  ' + self.run_name + '\n'
        for name in print_variables:
            string += space + '  ' + name + ' = ' + str(getattr(self, name)) + '\n'
        return string
        
    def _get_run_name(self):
        (path, name) = os.path.split(os.path.expanduser(self.parm_file))
        run_name, file_ext = os.path.splitext(name)
        return run_name

    def default_print_variables(self, exclude=[]):
        '''
        Returns default variables to print and edit, and excludes the list
        of variables *exclude* from the list
        '''
        print_variables = self.editable_traits()
        print_variables.remove('output_variables')
        print_variables.remove('print_variables')
        print_variables.remove('edit_exclude_variables')
        print_variables.remove('app_type')
        print_variables.remove('app_version')
        print_variables.remove('app_version_number')
        print_variables.remove('run_name')
        for variable in exclude:
            if variable in print_variables:
                print_variables.remove(variable)
        return print_variables
        
    def default_output_variables(self, exclude=[]):
        '''
        Returns the default variables to output to the saved state, and excludes 
        the list of variables *exclude* from the list
        '''
        output_variables = self.editable_traits()
        output_variables.remove('output_variables')
        output_variables.remove('print_variables')
        output_variables.remove('edit_exclude_variables')
        output_variables.remove('parm_file')
        output_variables.remove('run_name')
        for variable in exclude:
            if variable in output_variables:
                output_variables.remove(variable)
        return output_variables
    
    def save_figs(self, name=None):
        '''
        Saves all the open figs to the *output_directory* in PNG format with a root
        name of *name*
        '''
        if not name:
            file_root = 'fig'
        else:
            file_root = name + '_fig'
        for i in plt.get_fignums():
            plt.figure(i)
            plt.savefig(expanduser(join(self.output_directory, file_root + '_%d.png' % i )))
       
    def default_output_path(self, create_only=False):
        '''
        Forms the default path for output of the results (~/tmp/output_directory_app_type_app_version_run_name/),
        then creates that directory if it does not exist and erases if it does exist (be careful).
        If *create_only*, it only creates it and erases if it does exist.
        '''
        if create_only:
            path = self.output_directory
        else:
            path = join('~','tmp','output_directory_' + self.app_type + '_' + self.app_version + '_' + self.run_name)
            self.output_directory = path
        
        # delete and create
        path = expanduser(path)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
              
    def list(self):
        self.print_traits()
        
    def print_parms(self):
        print(self)
        
    def convert_parm(self, data_dict):
        '''
        converts the parameters from older versions
        ##### need to be extended with version specific code #####
        '''
        print('converted v' + data_dict['app_version'] + ' to v' + self.app_version)
        data_dict['app_version'] = self.app_version
        data_dict['app_version_number'] = self.app_version_number
        
    def save(self, parm_file=None):
        '''
        Saves all the parameters to a compressed binary numpy file (NPZ file), *parm_file* 
        (default self.parm_file). This is not meant for large data, only meta data.
        The list of parameters saved is self.output_variables (default list is
        self.default_output_variables())
        '''
        if not parm_file:
            parm_file = self.parm_file
        if not self.output_variables:
            output_variables = self.default_output_variables()
        else:
            output_variables = self.output_variables
        
        save_list = {}    
        for name in output_variables:
            save_list[name] = getattr(self, name)
        np.savez(str(expanduser(parm_file)), **save_list)
        
    def load(self, parm_file=None):
        '''
        Loads all the parameters from a compressed binary numpy file (NPZ file), *parm_file* 
        (default self.parm_file). This is not meant for large data, only meta data.
        Checks that the app_type is correct and calls self.convert_parm if the app_version 
        has changed.
        '''
        if not parm_file:
            parm_file = self.parm_file

        data = np.load(str(expanduser(parm_file)), allow_pickle=True)
        data_dict = {}
        for attribute, value in data.items():
            data_dict[attribute] = value.tolist()
            setattr(self, attribute, value.tolist())
            
        if not ('app_type' in data_dict):
            data_dict['app_type'] = self.app_type
            data_dict['app_version'] = '0'
            data_dict['app_version_number'] = 0
            print('File does not have an app_type,  Setting it to ' + self.app_type)
                            
        if self.app_type == data_dict['app_type']:
            if self.app_version != data_dict['app_version']:
                self.convert_parm(data_dict)
            for attribute, value in data.items():
                setattr(self, attribute, data_dict[attribute])
        else:
            print('Not able to load parameters. Wrong app_type ' + data_dict['app_type'])
    
    #### define all the buttons for the GUI ####
    save_button = Button('Save parameters')
    def _save_button_fired(self):
        self.save()
        
    load_button = Button('Load parameters')
    def _load_button_fired(self):
        self.load() 
        
    print_button = Button('Print parameters')
    def _print_button_fired(self):
        self.print_parms()  
         
    set_output_directory_button = Button('Set/Create output directory')
    def _set_output_directory_button_fired(self):
        self.default_output_path()
        
    run_button = Button('Run')
    def _run_button_fired(self):
        self.default_output_path(create_only=True)
        self.run()
        
    plot_button = Button('Plot')
    def _plot_button_fired(self):
        self.plot() 
        
    save_plots_button = Button('Save plots')
    def _save_plots_button_fired(self):
        self.save_figs()
                                                                                              
    def _traits_tab_view(self, parm_variables):
        from traitsui.api import View, Group, Item, ListEditor, UItem, TextEditor, SetEditor, Tabbed
        from traitsui.menu import HelpButton

        exclude=['output_directory','description','parm_file']
        for variable in exclude:
            if variable in parm_variables:
                parm_variables.remove(variable)
                
        run_group = Group(
                    UItem('run_button'), UItem('plot_button'),
                    UItem('save_plots_button'),
                    label = 'run')
        parm_group = Group(
                    list(parm_variables),
                    label = 'parameters')
        file_group = Group(
                    Item('app_type', style='readonly'), Item('app_version', style='readonly'),
                    '_',
                    Item('run_name', style='readonly'),
                    '_',
                    'parm_file',
                    UItem('save_button'), UItem('load_button'), UItem('print_button'),
                    '_',
                    'output_directory', UItem('set_output_directory_button'),
                    '_',
                    Item('description', label='Description:',style='custom', height=10),
                    label = 'file')
        traits_tab_view = View(Tabbed(file_group, parm_group, run_group),
                    title = self.app_type + ' v' + self.app_version,
                    width = 600,
                    height=800,
                    resizable=True,
                    buttons=[HelpButton],
                    )
        return traits_tab_view
        
    def edit(self):
        '''
        This envokes a GUI editor of all the variables in self.print_variables
        (default list is self.default_print_variables()).
        '''
        
        if not self.print_variables:
            parm_variables = self.default_print_variables()
        else:
            parm_variables = self.print_variables.copy()
               
        self.edit_traits(self._traits_tab_view(parm_variables), scrollable=True)
        
    def edit_restricted(self):
        '''
        This envokes a restricted GUI editor of all the variables in self.print_variables
        except for those in the list self.edit_exclude_variables,
        (default self.print_variables is self.default_print_variables()).
        '''
        
        if not self.print_variables:
            parm_variables = self.default_print_variables()
        else:
            parm_variables = self.print_variables.copy()
        for variable in self.edit_exclude_variables:
            if variable in parm_variables:
                parm_variables.remove(variable)
                        
        self.edit_traits(self._traits_tab_view(parm_variables), scrollable=True)
        
    def run(self):
        '''
        does the work, the core of the calculation
        ##### need to be replaced with app specific code #####
        '''
        pass
        
    def plot(self):
        '''
        plot the results of the calculation
        ##### need to be replaced with app specific code #####
        '''
        pass

                                                                
class DemoApp(AppRunner):
    '''
    This is a simple example of how to use and extend the **AppRunner** class
    '''
    
    parm1 = CFloat(3.0)
    parm2 = Enum(['a','b','c'])
    parm3 = CInt(2)
    parm4 = Bool(True)
    parm_new = CFloat(2.0)  #new parameter for v1
    parm_hidden = Str("I'm hidden")
    parm_noedit = Str("Don't edit me")
    
    def app_type_version(self):
        return 'DemoApp', '1_0', 1.0
        
    def __init__(self, *args, **kwargs): 
        self.parm2 = 'c'   # default value
        self.print_variables = self.default_print_variables(exclude=['parm_hidden'])
        self.edit_exclude_variables = ['parm_noedit']
        
        AppRunner.__init__(self, *args, **kwargs)
        
    def convert_parm(self, data_dict):
        old_version_number = data_dict['app_version_number']
        new_version_number = self.app_version_number
        if old_version_number < 1.0:
            self.parm_new = data_dict['parm1']  # parm_new did not exist before v1, default=parm1
        
        AppRunner.convert_parm(self, data_dict)
                
    def run(self):
        print(self.parm1, self.parm2, self.parm3, self.parm_new)
        
    def plot(self):
        x = np.linspace(0.0,5.0,50)
        y = self.parm1 * x * x - self.parm_new * x
        
        plt.figure()
        plt.plot(y,x)
        plt.title('output of ' + self.app_type + ', run name ' + self.run_name)
        plt.xlabel('X')
        plt.ylabel('Y')

def run_app_runner():
    '''
    Master procedure that evokes the AppRunner editor
    '''
    from meglib.app_runner import AppRunner
    
    p = AppRunner()
    p.edit()
    return p
            
def test_app_runner():
    '''
    Some test commands on the use of the **AppRunner** and **DemoApp** classes
    '''
    from os.path import expanduser, join
    from meglib.app_runner_v3 import AppRunner, DemoApp, run_app_runner
    import matplotlib.pyplot as plt
    
    # print, edit, and save a AppRunner object
    p = AppRunner()
    print(p)
    p.list()
    p.edit()
    p.parm_file = join('~','tmp','test_1.npz')
    p.save()
    
    # load, run, plot and save the figures as PNG of the previously saved AppRunner object
    p=AppRunner(parm_file=join('~','tmp','test_1.npz'))
    p.default_output_path()
    p.run()
    p.plot()
    p.save_figs()
    
    # open up and run AppRunner
    run_app_runner()
    
    # print, edit, and save a DemoApp object
    p = DemoApp()
    print(p)
    p.edit()
    p.parm_file = join('~','tmp','test_2.npz')
    p.save()
    
    # load, run, plot and save the figures as PNG of the previously saved DemoApp object
    p=DemoApp(parm_file=join('~','tmp','test_2.npz'))
    p.parm1=300.0
    p.parm2='b'
    print(p)
    p.default_output_path()
    p.run()
    p.plot()
    p.save_figs()
    