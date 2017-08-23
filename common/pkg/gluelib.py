#
# ===========================================================================
#
#                            PUBLIC DOMAIN NOTICE
#               National Center for Biotechnology Information
#
#  This software/database is a "United States Government Work" under the
#  terms of the United States Copyright Act.  It was written as part of
#  the author's official duties as a United States Government employee and
#  thus cannot be copyrighted.  This software/database is freely available
#  to the public for use. The National Library of Medicine and the U.S.
#  Government have not placed any restriction on its use or reproduction.
#
#  Although all reasonable efforts have been taken to ensure the accuracy
#  and reliability of the software and data, the NLM and the U.S.
#  Government do not and cannot warrant the performance or results that
#  may be obtained by using this software or data. The NLM and the U.S.
#  Government disclaim all warranties, express or implied, including
#  warranties of performance, merchantability or fitness for any particular
#  purpose.
#
#  Please cite the author in any work or product based on this material.
#
# ===========================================================================
#
# Code author:  Alexander Bliskovsky
#

"Code for handling dependency resolution."""
from ..utils import dataobj
from ..utils.filesys import makedirs2
import datetime
from collections import defaultdict
from progressbar import ProgressBar as PBar
import copy
import os
import hashlib
import shutil
from os import path

def get_hash(objects):
    """Return an hex representation of the MD5 hash of a list of objects"""
    digest = hashlib.md5()

    for some_object in objects:
        digest.update(str(some_object))

    return digest.hexdigest()


def get_module(mod_path):
    """Dynamically imports a dotted module."""
    mod_list = mod_path.split('.')
    mod = __import__(mod_path)
    mod_list.pop(0)
    while mod_list:
        mod = getattr(mod, mod_list.pop(0))

    return mod

def load_object(module_name, class_name, imported_modules):
    if module_name not in imported_modules:
        imported_modules[module_name] = get_module(module_name)

    class_object = getattr(imported_modules[module_name],
                           class_name)

    return class_object

def config2dict(data_object):
    name2info = {}
    for entry in data_object['dep_list']:
        entry_dict = {}
        name = None
        for field, data in entry:
            if field == 'name':
                name = data
            elif field == 'args':
                entry_dict['args'] = data
            else:
                entry_dict[field] = data
        name2info[name] = entry_dict

    return name2info

def dict2config(data_object):
    config_dict = {'dep_list': []}

    # The name field is omitted here because that is referenced by
    # the dictionary key.
    field_order = ['docstring', 'dep_node_module','dep_node_class',
                   'hidden', 'prereqs', 'args']
    for entry in data_object:

        entry_fields = []
        entry_fields.append(['name', entry])
        for field in field_order:
            entry_fields.append([field, data_object[entry][field]])

        config_dict['dep_list'].append(entry_fields)

    return config_dict

def calculate_node2dependents(name2info):
    '''Calculate dependents of each node.'''
    node2dependents = defaultdict(set)

    for node in name2info:
        dependents = name2info[node]['prereqs']

        for dependent in dependents:
            node2dependents[dependent].add(node)

    return node2dependents


class DependencyError(Exception):
    """Thrown when a node to be deleted still has dependents."""
    def __init__(self, desc):
        self.desc = desc
        Exception.__init__(self, 'Dependency Error: {0}'.format(desc))


class DepGraph(object):
    """Stores a representation of a dependency graph read from a json file.
    """

    def __init__(self, desired_product, json_config_file, **kwargs):
        """Reads the configuration file and creates a topologically
        sorted stack from which to resolve dependencies.

        Arguments:
        - `json_config_file`: The dependency configuration file in json
                              format with a dictionary that contains dep_list,
                              a list of all dependencies with a list of the
                              following:
                               - name: the name of the dependency node
                               - class: the name of the class to be
                                        initialized.
                               - prerequisites: a list of names of prereqs.
                               - module: the module in which the task function
                                         resides.

        - `desired_prodict`: The name of the dependency module that will serve
                             as the final product.
        """

        self._dep_dict = {}
        self.topological_order = []
        self.visited_nodes = []
        self.imported_modules = {}
        self.name2info = {}
        self.kwargs = kwargs
        self.product = desired_product
        self.to_be_copied = set()
        self.install_dir = self.kwargs.get('_install_dir', os.getcwd())
        self.verbose = self.kwargs.get('verbose', 1)
        self.ignored_entries = ['files', 'all']

        if not os.path.exists('dep_config.json'):
            shutil.copy(json_config_file, 'dep_config.json')

        config = dataobj.restore_data_object('dep_config.json')

        try:
            self.database = \
                dataobj.restore_data_object('installation_database.json')
        except IOError:
            self.database = {}

        for entry in config['dep_list']:
            entry_dict = {}
            name = None
            for field, data in entry:
                if field == 'name':
                    name = data
                elif field == 'args':
                    data.update({'_install_dir': ''})
                    entry_dict['args'] = data
                else:
                    entry_dict[field] = data
            if entry_dict['dep_node_class'] == 'DepURLFile':
                entry_dict['args'].update({'get_from': \
                                           self.kwargs.get('get_from',
                                                           None)})
            self.name2info[name] = entry_dict

        for name in self.name2info:
            node_info = self.name2info[name]

            if node_info['prereqs'] == None:
                node_info['prereqs'] = []
            try:
                deps  = set(self.database[name]['dependents'])
            except KeyError:
                deps = set()

            node_info['dependents'] = deps

            node_info['hash'] = get_hash((name, node_info['args']))
            node_info['visits'] = 0

            self.name2info[name] = node_info
        try:
            self.visit_node(desired_product)
        except KeyError as strerror:
            raise DependencyError('A node was not found. Either the dependency' +
                                   ' database is corrupted\nor a non-existent node' +
                                   ' was specified. ({0})'.format(strerror))
        self.calculate_new_dependents()

    def calculate_new_dependents(self):
        '''Get installed dependents'''
        node2dependents = calculate_node2dependents(self.name2info)

        for node in self.topological_order:
            node_dependents = node2dependents[node]
            new_dependents = set()

            for nd in node_dependents:
                if nd in self.topological_order:
                    new_dependents.add(nd)

            self.name2info[node]['dependents'].update(new_dependents)

    def _load_classes(self):
        # Load all classes here in topological order and
        # add them to _dep_dict.
        dep_stack = self.topological_order

        for name in dep_stack:
            module_name = self.name2info[name]['dep_node_module']
            class_name = self.name2info[name]['dep_node_class']

            class_object = load_object(module_name, class_name,
                                       self.imported_modules)

            if self.name2info[name]['args']:
                obj = class_object(False, self, name, self.verbose,
                                   **self.name2info[name]['args'])
            else:
                obj = class_object(False, self,
                                   name, self.verbose)

            self._dep_dict[name] = obj

    def _load_classes_from_list(self, node_list):
        for name in node_list:
            module_name = self.name2info[name]['dep_node_module']
            class_name = self.name2info[name]['dep_node_class']

            class_object = load_object(module_name, class_name,
                                       self.imported_modules)

            if self.name2info[name]['args']:
                obj = class_object(False, self, name, self.verbose,
                                   **self.name2info[name]['args'])
            else:
                obj = class_object(False, self,
                                   name, self.verbose)

            self._dep_dict[name] = obj

    def visit_node(self, node_name, search_stack=None):
        """Recursive topological sort."""
        if search_stack is None:
            search_stack = []
        else:
            search_stack = copy.copy(search_stack)

        # If the node sees itself in the current stack,
        # that means that something that the node depends
        # on depends on it, which indicates a cycle.
        if node_name in search_stack:
            raise Exception("Graph is not acyclic.")
        else:
            search_stack.append(node_name)

        if node_name != self.product:
            self.name2info[node_name]['visits'] += 1

        if node_name not in self.visited_nodes:
            self.visited_nodes.append(node_name)
            for edge in self.name2info[node_name]['prereqs']:
                self.visit_node(edge, search_stack)

            self.topological_order.append(node_name)

    def install_all(self):
        """Visit all root nodes and install them."""
        for node in self.name2info:
            if self.name2info[node]['hidden'] == False:
                self.visit_node(node)

        self.calculate_new_dependents()
        self.resolve_dependencies()

    def verify_all(self):
        '''Run an integrity check on the installation.'''
        #This is here in case other things, such as files, need to be verified.
        self.check_postconditions()

    def check_postconditions(self):
        '''Check all postconditions for all installed nodes.'''
        for node in self.name2info:
            self.visit_node(node)

        self._load_classes()

        changed_nodes = []

        for node in self.database:
            if node[0] != '_' and node not in self.ignored_entries:
                res = self._dep_dict[node].verify()
                if res == 'reconfigured':
                    changed_nodes.append(node)

        self._update_installation_database('install', changed_nodes)

    def get_status(self, node):
        """Return the status of the node."""
        node_info = self.name2info[node]

        try:
            lifetime = int(self.database['_config']['lifetime'])
        except KeyError:
            lifetime = 30

        if node not in self.database:
            return 'not_present'

        current_date = datetime.datetime.today()
        old_date = datetime.datetime.strptime(self.database[node]['date'],
                                              '%Y-%m-%d')

        if current_date - old_date >= datetime.timedelta(lifetime):
            return 'date_mismatch'

        return 'current'

    def resolve_dependencies(self):
        """Run all tasks in order of topology."""
        dep_stack = copy.copy(self.topological_order)
        self._load_classes()

        if self.verbose == 1:
            print 'Installation of {0}:'.format(self.product)
            pbar = PBar(maxval = len(self.topological_order)).start()
        nodes_done = 0

        new_nodes = []
        touched_nodes = []
        while len(dep_stack) > 0:
            current_job = dep_stack.pop(0)
            if not current_job in self.database:
                self._dep_dict[current_job].resolve()
                if self._dep_dict[current_job].state == 'RESOLVED':
                    self.to_be_copied.update(
                        self._dep_dict[current_job].to_be_copied)
                    new_nodes.append(current_job)
                    self.process_to_be_copied()
                    nodes_done +=1
                    if self.verbose == 1:
                        pbar.update(nodes_done)

            else:
                touched_nodes.append(current_job)

        self._update_installation_database('install', new_nodes)
        self._update_installation_database('update', touched_nodes)
        if self.verbose == 1:
            pbar.finish()

    def process_to_be_copied(self):
        """Convert absolute paths to relative."""
        proc_to_be_copied = set()

        for file_path in self.to_be_copied:
            filename = os.path.relpath(file_path, self.install_dir)
            proc_to_be_copied.add(filename)

        self.to_be_copied = proc_to_be_copied

    def remove_tree(self, forced):
        """Remove a node with traversal."""

        self._load_classes()
        if len(self.name2info[self.product]['dependents']) > 0 and not forced:
            print "{0} still has dependents. Not Removing.".format(self.product)
            return

        for node in self.topological_order:
            self.name2info[node]['dependents'] = self.name2info[node]['dependents'] - \
                                                 set(self.topological_order)

        keys_to_delete = []
        keys_to_update = []
        for key in self.name2info:
            if key in self._dep_dict:
                if len(self.name2info[key]['dependents']) == 0 or forced:
                    keys_to_delete.append(key)
                else:
                    keys_to_update.append(key)

        for key in keys_to_delete:
            self._dep_dict[key].remove()

        self._update_installation_database('remove', keys_to_delete)
        self._update_installation_database('update', keys_to_update)

    def _update_installation_database(self, action, objects):
        """Write to the installtion database."""

        if action == 'install':
            for node in objects:
                db_args = [arg for arg in \
                           self.name2info[node]['args'] if arg[0] != '_']

                args_to_write = {}

                for key in db_args:
                    args_to_write[key] = self.name2info[node]['args'][key]

                node_hash = get_hash((node, self.name2info[node]['args']))

                node_dict = {'hash': node_hash,
                             'date': str(datetime.date.today()),
                             'arguments': args_to_write,
                             'dependents': list(self.name2info[node]['dependents'])
                             }
                self.database[node] = node_dict
            file_set = set(self.database.get('files', []))
            file_set.update(self.to_be_copied)
            self.database['files'] = list(file_set)
        elif action == 'remove':
            for node in objects:
                try:
                    del self.database[node]
                except KeyError:
                    pass

            file_set = set(self.database.get('files', []))

            # Remove any files that no longer exist
            nonexistant_files = set()
            for file_name in file_set:
                if not os.path.exists(file_name):
                    nonexistant_files.add(file_name)

            file_set = file_set - nonexistant_files
            self.database['files'] = list(file_set)
        elif action == 'update':
            for node in objects:
                self.database[node]['dependents'] = \
                     list(self.name2info[node]['dependents'])
                self.database[node]['date'] = str(datetime.date.today())

        path_to_db = 'installation_database.json'
        dataobj.save_data_object(self.database, path_to_db)

    def remove(self, forced):
        """Remove a node without traversal."""
        self._load_classes()

        if forced:
            self._dep_dict[self.product].remove()

        elif len(self.name2info[self.product]['dependents']) > 0:
            raise DependencyError('This node still has dependents. Use -f to force.')

        else:
            self._dep_dict[self.product].remove()

        self._update_installation_database('remove', [self.product])

    def upgrade(self):
        """Call the update function of each class."""
        self._load_classes()

        print self.topological_order

        for name in self.topological_order:
            self._dep_dict[name].upgrade()

        self._update_installation_database('update',
                                           self.topological_order)

    def get_info(self):
        """Return a list of nodes and relevant info."""

        info_list = []

        for name in self.topological_order:
            node_info = self.name2info[name]
            info_list.append((name,
                              node_info['docstring'],
                              node_info['hidden'],
                              self.get_status(name)))

        return info_list

    def list_all_deps(self):
        """Return a list of all nodes and relevant info."""

        info_list = []

        for name in self.name2info:
            node_info = self.name2info[name]
            info_list.append((name,
                              node_info['docstring'],
                              node_info['hidden'],
                              self.get_status(name)))

        return info_list


class DepNode(object):
    """A base class for all dependency nodes."""

    def __init__(self, optional, parent_graph, name, verbose, **kwargs):
        self.optional = optional

        self.state = 'UNRESOLVED'
        self.to_be_copied = set()

        self.kwargs = kwargs
        self._v_level = verbose

        self.__dict__.update(self.kwargs)
        self.parent_graph = parent_graph
        self.name = name

    def printmsg(self, msg, v_level):
        """Verbosity level handler."""

        if v_level <= self._v_level:
            print msg

    def resolve(self):
        """Perform the tasks needed to resolve a dependency."""
        pass

    def remove(self):
        """Uninstall the dependency."""
        pass

    def upgrade(self):
        """Update the dependency."""
        pass

    def verify(self):
        """Check to make sure all postconditions are true."""
        pass

    @staticmethod
    def _add_storage_dir(storage_dir, kwopts, keys):
        # Utility to append directory to filenames
        if storage_dir:
            makedirs2(storage_dir)
            for k in keys:
                kwopts[k] = os.path.join(storage_dir, kwopts[k])
