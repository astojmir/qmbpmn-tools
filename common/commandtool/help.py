"""\
An example program which scans an existing module written with commandtool
and generates a reStructuredText file from the docstrings. That file can
then be converted to HTML or a man page with other commands.
"""

import sys

try:
    import docutils
except ImportError:
    print "Please install docutils"
    sys.exit(1)

# manpage.py 5901 2009-04-07 13:26:48Z grubert $
# Author: Engelbert Gruber <grubert@users.sourceforge.net>
# The manpage module is put into the public domain so can
# be included here. Thanks Engelbert!
import qmbpmn.common.commandtool.manpage as manpage

import getopt
import logging
import os.path
import StringIO
import os
import subprocess

from qmbpmn.common.commandtool import parse_html_config
from qmbpmn.common.commandtool import makeHandler
from qmbpmn.common.commandtool import strip_docstring
from qmbpmn.common.commandtool import option_names_from_option_list
from qmbpmn.common.commandtool import set_error_on
from qmbpmn.common.commandtool import parse_command_line
from qmbpmn.common.commandtool import make_man_page
from qmbpmn.common.commandtool import handle_program
from qmbpmn.common.commandtool import help_strings

from docutils import core
from docutils.writers.html4css1 import Writer as HTMLWriter, HTMLTranslator

log = logging.getLogger(__name__)

option_sets = {
    'synopsis': [
        dict(
            type = 'command',
            long = ['--synopsis'],
            short = ['-S'],
            metavar = 'SYNOPSIS',
        ),
    ],
    'group': [
        dict(
            type = 'command',
            long = ['--group'],
            short = ['-g'],
            metavar = 'GROUP',
        ),
    ],
    'rest': [
        dict(
            type = 'command',
            long = ['--rest'],
            short = ['-r'],
            metavar = 'REST',
        ),
    ],
    'copyright': [
        dict(
            type = 'command',
            long = ['--copyright'],
            short = ['-c'],
            metavar = 'COPYRIGHT',
        ),
    ],
    'options': [
        dict(
            type = 'command',
            long = ['--options'],
            short = ['-O'],
            metavar = 'OPTIONS',
        ),
    ],
    'date': [
        dict(
            type = 'command',
            long = ['--date'],
            short = ['-D'],
            metavar = 'DATE',
        ),
    ],
    'address': [
        dict(
            type = 'command',
            long = ['--address'],
            short = ['-a'],
            metavar = 'ADDRESS',
        ),
    ],
    'organization': [
        dict(
            type = 'command',
            long = ['--organization'],
            short = ['-o'],
            metavar = 'ORGANISATION',
        ),
    ],
    'description': [
        dict(
            type = 'command',
            long = ['--description'],
            short = ['-d'],
            metavar = 'EMAIL',
        ),
    ],
    'section': [
        dict(
            type = 'command',
            long = ['--section'],
            short = ['-i'],
            metavar = 'SECTION',
        ),
    ],
    'program_description': [
        dict(
            type = 'command',
            long = ['--program-description'],
            short = ['-s'],
            metavar = 'EMAIL',
        ),
    ],
    'email': [
        dict(
            type = 'command',
            long = ['--email'],
            short = ['-e'],
            metavar = 'EMAIL',
        ),
    ],
    'version': [
        dict(
            type = 'command',
            long = ['--version'],
            short = ['-V'],
            metavar = 'VERSION',
        ),
    ],
    'help': [
        dict(
            type = 'shared',
            long = ['--help'],
            short = ['-h'],
        ),
    ],
    'verbose': [
        dict(
            type = 'program',
            long = ['--verbose'],
            short = ['-v'],
        ),
        dict(
            type = 'program',
            long = ['--quiet'],
            short = ['-q'],
        ),
    ]
}

aliases = {
    'rst2man': [],
    'commands2rst': [],
    'commands2help': [],
}

class CustomHTMLTranslator(HTMLTranslator):
    def __init__(self, *k, **p):
        HTMLTranslator.__init__(self, *k, **p)
        # Allow long field names more than 14 characters in reStructuredText
        # field lists
        self.settings.field_name_limit = 0

def rstify2html(string):
    w = HTMLWriter()
    w.translator_class = CustomHTMLTranslator
    result = core.publish_parts(string, writer=w)
    # Strip the first and last lines
    return result

def rstify2man(string, path):
    """
    Turn a reSturcturedText string into HTML, capturing any errors or warnings
    and re-emitting them with this programs logging system.
    """
    # Temporarily capture stderr and stdout
    err = sys.stderr
    out = sys.stdout
    error = ''
    out_msg = ''
    try:
        sys.stderr = StringIO.StringIO()
        sys.stdout = StringIO.StringIO()
        w = manpage.Writer()
        result = core.publish_parts(string, writer=w)
        error = sys.stderr.getvalue()
        out_msg = sys.stdout.getvalue()
    finally:
        sys.stderr = err
        sys.stdout = out
    if error:
        log.warning('%s - %s', path, error.replace('\n', ' '))
    if out_msg:
        log.warning('%s - %s', path, out_msg.replace('\n', ' '))
    return result['whole']

def handle_command_rst2man(
    option_sets,
    command_options,
    args
):
    """\
    usage: ``%(program)s [PROGRAM_OPTIONS] man NAME``

    Convert a ``.rst`` file into a man page. If a directory called ``man1``
    exists in the same directory as ``NAME``, the man file is gzipped and put
    inside that directory so you can test it by running this command in the current
    working directory where COMMAND is the the the same as NAME without the
    ``.rst`` extensions:

      ``man -M ./ COMMAND``

    Arguments:

      :``NAME``: The .rst file to convert to a man page

    Options:

      All ``PROGRAM_OPTIONS`` (see \`%(program)s --help')
    """
    set_error_on(
        command_options,
        allowed=['config', 'start_directory']
    )
    config = {}
    if command_options.has_key('config'):
        config = command_options['config'][0]['handled']
    internal_vars = {}
    if not len(args):
        raise getopt.GetoptError('No NAME specified')
    elif len(args)>1:
        raise getopt.GetoptError('Got unexpected argument %r'%args[1])
    fp = open(args[0], 'r')
    data = fp.read()
    fp.close()
    try:
        data = rstify2man(data, args[0])
    except Exception, e:
        print "FAILED: %s"%(str(e))
        print "Please check the reStructuredText in %s can be converted by rst2html.py without warnings"%args[0]
    else:
        file = args[0].split('.')[0]+'.1'
        fp = open(file, 'w')
        fp.write(data)
        fp.close()

        os.system('gzip %s'%(file))
        if os.path.exists('man1'):
            os.system('mv %s.gz man1'%file)
            print "Now run 'man -M ./ %s'"%args[0][:-4]

def handle_command_commands2help(
    option_sets,
    command_options,
    args
):
    """\
    usage: ``%(program)s [PROGRAM_OPTIONS] MODULE_PATH OUTPUT``

    Scan a Python module containing commandtool commands handlers and extract
    the docstrings. Process them using ``elinks`` and save them to ``OUTPUT`` so
    taht they can be imported by a program to print help output on the command
    line.

    Arguments:

      :``MODULE_PATH``:  The Python module path to the module to scan. eg: ``some.sub.module``
      :``OUTPUT``:       The filename of a Python file to save the formatted help text in

    Options:

      All ``PROGRAM_OPTIONS`` (see \`%(program)s --help')
    """
    internal_vars = set_error_on(
        command_options,
        allowed=[
        ]
    )
    if not len(args):
        raise getopt.GetoptError('No MODULE_PATH specified')
    if not len(args)>1:
        raise getopt.GetoptError('No OUTPUT specified')
    if len(args)>2:
        raise getopt.GetoptError('Got unexpected argument %r'%args[2])

    module = __import__(args[0])
    parts = args[0].split('.')[1:]
    for part in parts:
        module = getattr(module, part)
    names = module.command_handler_factories.keys()
    description = []

    def handle(input):
        input = rstify2html(input)['whole'].replace('<th ', '<td ')
        cmd = 'elinks -force-html -dump'
        args = cmd.split(' ')
        process = subprocess.Popen(args, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        data = process.communicate(input.encode('utf-8'))
        return data[0]

    for k in names:
        description.append(k+'="""')
        content = strip_docstring(module.command_handler_factories[k]().__doc__)
        description.append(strip_docstring(handle(content)))
        description.append('"""\n\n')
    description.append('__program__="""')
    description.append(strip_docstring(handle(module.program_help)))
    description.append('"""\n\n')
    data = ''.join(description)
    fp = open(args[1], 'w')
    fp.write('# -*- coding: utf-8 -*-\n\n')
    fp.write(data)
    fp.close()
    print "Saved to %s."%args[1]

def handle_command_commands2rst(
    option_sets,
    command_options,
    args
):
    """\
    usage: ``%(program)s [PROGRAM_OPTIONS] commands2rst MODULE_PATH COMMAND_NAME``

    Extract docstrings from ``MODULE_PATH`` to create rst file named ``COMMAND_NAME.rst`` for the program ``COMMAND_NAME``

    Arguments:

      :``MODULE_PATH``:  The Python module path to the module to scan. eg: ``some.sub.module``
      :``COMMAND_NAME``: The command line name of the program the documentation is for

    Options:

      -e, --email                 author email
      -V, --version               software version
      -s, --program-description   one line program description
      -d, --description           full description
      -o, --organization          organization name
      -O, --options               options
      -a, --address               organization address
      -D, --date                  date (defaults to current date if not specified)
      -c, --copyright             copyright
      -t, --rest                  extra information to add
      -S, --synopsis              program synopsis
      -g, --group                 man group (defaults to text processing)
      -i, --section               man page section number (defaults to 1)

      Plus all ``PROGRAM_OPTIONS`` (see \`%(program)s --help')
    """
    internal_vars = set_error_on(
        command_options,
        allowed=[
            'email',
            'version',
            'section',
            'program_description',
            'description',
            'organization',
            'address',
            'date',
            'copyright',
            'rest',
            'group',
            'synopsis',
            'options',
        ]
    )
    if not len(args):
        raise getopt.GetoptError('No MODULE_PATH specified')
    if not len(args)>1:
        raise getopt.GetoptError('No COMMAND_NAME specified')
    if len(args)>2:
        raise getopt.GetoptError('Got unexpected argument %r'%args[2])
    module = __import__(args[0])
    parts = args[0].split('.')[1:]
    for part in parts:
        module = getattr(module, part)
    names = module.command_handler_factories.keys()
    description = ['SUB-COMMANDS\n============\n\n']
    names.sort()
    for k in names:
        description.append('``'+k+'``')
        description.append('')
        for line in strip_docstring(
            module.command_handler_factories[k]().__doc__%{'program':args[1]}
        ).encode('utf-8').split('\n'):
            description.append('  '+line)
        description.append('\n')
    internal_vars['program_name'] = args[1]
    internal_vars['synopsis'] =  internal_vars.get('synopsis', '') + strip_docstring(
        module.handle_program.__doc__%{'program':args[1]}
    )
    internal_vars['rest'] = internal_vars.get('rest', '') + '\n' + \
       '\n'.join(description)
    data = make_man_page(**internal_vars)
    fp = open(args[1]+'.rst', 'w')
    fp.write(data)
    fp.close()
    print "Done."

command_handler_factories = {
    'rst2man': makeHandler(handle_command_rst2man),
    'commands2help': makeHandler(handle_command_commands2help),
    'commands2rst': makeHandler(handle_command_commands2rst),
}

program_help = """\
usage: ``%(program)s [PROGRAM_OPTIONS] COMMAND [OPTIONS] ARGS``

Commands (aliases):

 :commands2help:  generate txt versions of the help text
 :commands2rst:   create an rst file from the docstrings in a module
 :rst2man:        generate a manpage from the generated rst file

Try \`%(program)s COMMAND --help' for help on a specific command.""",

if __name__ == '__main__':
    try:
        command = None
        prog_opts, command_opts, command, args = parse_command_line(
            option_sets,
            aliases,
        )
        handle_program(
            command_handler_factories,
            option_sets,
            aliases,
            prog_opts,
            command_opts,
            command,
            args,
            program_name = os.path.split(sys.argv[0])[1],
            help=help_strings,
        )

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        if command:
            print "Try `%(program)s %(command)s --help' for more information." % {
                'program': os.path.split(sys.argv[0])[1],
                'command': command,
            }
        else:
            print "Try `%(program)s --help' for more information." % {
                'program': os.path.split(sys.argv[0])[1],
            }
        sys.exit(2)

