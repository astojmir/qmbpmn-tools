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

"""
Manages dependencies.

SYNOPSIS:

   qmbpmn_datasets <command> [options] <dependency node>

COMMANDS:

   install      Install a dependency node and all nodes that it depends on.
                USAGE:
                  qmbpmn_datasets install [d dir |v ver] dependency-node-name

                OPTIONS:
                  -d: The directory in which to install the files. (Defaults
                      to current working directory.)
                  -v: Verbosity level in the range [1, 5], 1 being the least
                      verbose and 5 being most verbose. If this flag is
                      omitted it defaults to 1.

   remove       Remove a previously installed dependency node.
                USAGE:
                  qmbpmn_datasets remove [-f|t|v=] dependency-node-name

                OPTIONS:
                  -f|--force: remove the node even if there are nodes that
                              depend on it.

                  -t|--no-traversal: Do not delete the nodes that this node
                                     depends on, even if they have no other
                                     dependents.

                  -v: Verbosity level. See above.

   list         List dependency nodes for a certain installation package, or
                list all nodes in database and their states. States are as
                follows:

                NI: Not Installed
                NC: Not Current
                C:  Current

                USAGE:
                  qmbpmn_datasets list [-a|d] [dependency-node-name]

                OPTIONS:
                  -a: Show all nodes, including those marked as 'hidden'.
                  -d: Show the packages installed in the specified directory.

   update       Update your dependency database.

                USAGE:
                  qmbpmn_datasets update [-d dir] [source]


   upgrade      Upgrade old nodes.

                USAGE:
                  qmbpmn_datasets update [-d dir|-a]

                OPTIONS:
                  -d: The directory in which to install the files. (Defaults
                      to current working directory.)
                  -a: Upgrade all currently installed packages, regardless
                      of status.

   config       Configure the local repository.
                USAGE:
                  qmbpmn_datasets config [option] [value]

                Omit both fields to see the list of options.

   copy         Copy all installed nodes from one directory into another.

                USAGE:
                  qmbpmn_datasets copy [-d dir] <destination>

   help         Print this message.
"""

import sys
import getopt
import os
import urllib

from qmbpmn.common.pkg import gluelib
import shutil
from qmbpmn.common.utils import dataobj
from operator import itemgetter

_ERROR_MSG = 'Isufficient arguments.'

def get_args(argv, options, long_options, min_args_len):
    try:
        opts, args = getopt.getopt(argv, options, long_options)
        if len(args) < min_args_len:
            raise getopt.GetoptError('Insufficient arguments')
        return opts, args
    except getopt.GetoptError as strerror:
        print "Error: ", strerror
        sys.exit(2)

def make_dep_graph(install_candidate, args=None):
    current_dir, _ = os.path.split(__file__)
    dependency_db = os.path.join(current_dir, 'dep_config.json')

    try:
        if args:
            graph = gluelib.DepGraph(install_candidate, dependency_db, **args)
        else:
            graph = gluelib.DepGraph(install_candidate, dependency_db)
    except gluelib.DependencyError as strerror:
        print strerror
        sys.exit(2)

    return graph

def command_install(args):

    long_options = ['dry-run', 'directory=', 'get-from=', 'verbose']
    options = 'd:g:v:'

    opts, args = get_args(args, options, long_options, 0)

    dry_run = False
    dep_args = {}

    for o, a in opts:
        if o == '--dry-run':
            dry_run = True
        if o == '-d' or o == '--directory':
            dep_args['_install_dir'] = a
            os.chdir(os.path.normpath(a))
        if o == '-g' or o == '--get-from':
            dep_args['get_from'] = a
        if o == '-v' or o == '--verbose':
            level = int(a)
            if 0 <= level < 6:
                dep_args['verbose'] = level

    graph = None

    if not args or 'all' in args:
        graph = make_dep_graph('all', dep_args)
        graph.install_all()

    while args:


        current_arg = args.pop(0)
        graph = make_dep_graph(current_arg, dep_args)

        new_nodes = 0

        for node in graph.topological_order:
            if node not in graph.database:
                new_nodes += 1

        if new_nodes > 0:
            print 'The following packages will be installed:'

            for node in graph.topological_order:
                if not node in graph.database:
                    print "+ ", node

            if not dry_run:
                graph.resolve_dependencies()

            graph.verify_all()

        else:
            print "No new nodes to install."




def command_remove(args):

    forced = False
    no_traversal = False

    options = 'ftv:d:'
    long_options = ['force', 'no-traversal', 'verbose=']

    dep_args = {}

    opts, args = get_args(args, options, long_options, 0)

    for o, a in opts:
        if o == '-f' or o == '--force':
            forced = True
        elif o == '-t' or o == '--no-traversal':
            no_traversal = True
        elif o == '-v' or o == '--verbose':
            level = int(a)
            if 0 <= level < 6:
                dep_args['verbose'] = level
        elif o == '-d':
            dep_args['_install_dir'] = a
            os.chdir(os.path.normpath(a))

    while args:
        current_arg = args.pop(0)
        graph = make_dep_graph(current_arg, dep_args)

        if not no_traversal:
            print "The following components are candidates for removal:"

            for comp in graph.topological_order:
                print "- ", comp

        if no_traversal:
            try:
                graph.remove(forced)
            except gluelib.DependencyError as strerror:
                print strerror
                sys.exit(2)
        else:
            graph.remove_tree(forced)

def print_list(summary, show_all):

    line_length = 80
    name_width = 20
    desc_width = 52
    status_width = 4
    summary.sort(key=itemgetter(1))

    print '-'*line_length
    print 'Name'.ljust(name_width), 'Description'.ljust(desc_width),
    print 'State'.ljust(status_width)
    print '-'*line_length

    for name, desc, hidden, status in summary:
        if status == 'date_mismatch':
            status = 'NC'
        elif status == 'not_present':
            status = 'NI'
        else:
            status = 'C'

        if not hidden or show_all:
            print name.ljust(name_width), desc.ljust(desc_width),
            print status.ljust(status_width)

    print '-'*line_length

def command_list(args):
    options = 'ad:'
    long_options = ['show-all']

    opts, args = get_args(args, options, long_options, 0)

    show_all = False
    dep_args = {}

    for o, a in opts:
        if o == '-a':
            show_all = True
        elif o == '--show-all':
            show_all = True
        elif o == '-d':
            dep_args['_install_dir'] = a
            os.chdir(os.path.normpath(a))

    if len(args) > 0:
        candidate = args[0]
        graph = make_dep_graph(candidate, dep_args)

        summary = graph.get_info()

        print 'The following nodes are dependents of the selected node.'
        print_list(summary, show_all)

    else:
        graph = make_dep_graph('all', dep_args)
        summary = graph.list_all_deps()

        print 'The following are the nodes in the dependency database:'
        print_list(summary, show_all)


def command_upgrade(args):
    options = 'ad:v:'
    long_options = []

    opts, args = get_args(args, options, long_options, 0)

    forced = False
    update_all = False
    dep_args = {}

    for o, a in opts:
        if o == '-a':
            update_all = True
        if o == '-d':
            dep_args['_install_dir'] = a
            os.chdir(os.path.normpath(a))
        if o == '-v':
            dep_args['verbose'] = a

    if len(args) == 0:
        graph = make_dep_graph('all', dep_args)
        summary = graph.list_all_deps()

        nodes_to_update = set()
        nodes_updated = set()

        for name, _, _, status in summary:
            if status == 'date_mismatch':
                nodes_to_update.add(name)
            elif update_all and status != 'not_present':
                nodes_to_update.add(name)

        if len(nodes_to_update) > 0:
            print 'The following dependencies will be updated:'

            for node in nodes_to_update:
                print node

            cont = raw_input('Continue? (y/n): ')

            if cont == 'y':
                pass
            elif cont == 'n':
                sys.exit()
            else:
                print "Not valid option. Exting."
                sys.exit()
        else:
            print 'No dependencies require updating.'


        for node in nodes_to_update:
            graph = make_dep_graph(node, dep_args)

            if node in nodes_updated:
                continue

            graph.upgrade()
            nodes_updated.update(set(graph.topological_order))
    else:
        for arg in args:
            graph = make_dep_graph(arg, dep_args)
            print 'Upgrading {0}.'.format(arg)
            graph.upgrade()


def command_update(args):
    options = 'nob:d:'
    long_options = ['no-backup']

    opts, args = get_args(args, options, long_options, 0)

    overwrite = 'prompt'
    backup_file = 'dep_config.json.bak'

    try:
        config_update_source = \
            dataobj.restore_data_object('installation_database')['_config']['update_source']
    except:
        config_update_source = 'default_path'

    current_dir = os.getcwd()

    for o, a in opts:
        if o == '-d':
            current_dir = a

    if len(args) == 1:
        update_source = args[0]
    else:
        update_source = config_update_source


    dependency_db = os.path.join(current_dir, 'dep_config.json')
    backup_db = os.path.join(current_dir, backup_file)

    update_config_fp = urllib.urlopen(update_source)

    local_config = dataobj.restore_data_object(dependency_db)
    dataobj.save_data_object(local_config, backup_db)
    update_config = dataobj.restore_data_object(update_config_fp)

    local_dict = gluelib.config2dict(local_config)
    update_dict = gluelib.config2dict(update_config)

    local_dict.update(update_dict)

    local_config = gluelib.dict2config(local_dict)

    dataobj.save_data_object(local_config, dependency_db)

def command_copy(args):
    options = 'd:'
    long_options = []

    opts, args = get_args(args, options, long_options, 0)

    if len(args) != 1:
        print 'Usage: glue copy [-d dir] <destination>'
        sys.exit(2)

    dest_location = args[0]
    source_location = os.getcwd()

    for o, a in opts:
        if o == '-d':
            source_location = a


    install_db = 'installation_database.json'
    path_to_db = os.path.join(source_location, install_db)
    new_path_to_db = os.path.join(dest_location, install_db)
    files = dataobj.restore_data_object(path_to_db)['files']

    print 'Copying installation database... ',
    shutil.copy(path_to_db, new_path_to_db)
    print 'done.'

    for file_name in files:
        old_path = os.path.join(source_location, file_name)
        new_path = os.path.join(dest_location, file_name)

        print 'Copying {0}... '.format(file_name, new_path),
        shutil.copy(old_path, new_path)
        print 'done.'

def command_config(args):

    options = ''
    long_options = []

    opts, args = get_args(args, options, long_options, 0)

    db = dataobj.restore_data_object('installation_database.json')

    default_config = {'lifetime': 30,
                      'update_source': 'default path'}

    try:
        config = db['_config']
    except KeyError:
        config = default_config

    if len(args) == 0:
        print 'Option'.ljust(15), 'Value'.ljust(15)
        print '-'*30
        for key in config:
            print key.ljust(15), str(config[key]).ljust(15)
        print ''

    elif len(args) == 1:
        try:
            value = config[args[0]]
        except KeyError:
            print 'That configuration parameter could not be found.'
            sys.exit(2)

        print args[0], ': ', value

    elif len(args) == 2:
        config[args[0]] = args[1]
        db['_config'] = config

        dataobj.save_data_object(db, 'installation_database.json')



def command_help(args):
    print __doc__
    sys.exit()
