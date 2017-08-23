commands2help="""usage: %(program)s [PROGRAM_OPTIONS] MODULE_PATH OUTPUT

Scan a Python module containing commandtool commands handlers and extract
the docstrings. Process them using elinks and save them to OUTPUT so taht
they can be imported by a program to print help output on the command
line.

Arguments:

   MODULE_PATH:  The Python module path to the module to scan. eg: some.sub.module
   OUTPUT:       The filename of a Python file to save the formatted help
                 text in

Options:

  All PROGRAM_OPTIONS (see `%(program)s --help')
"""

commands2rst="""usage: %(program)s [PROGRAM_OPTIONS] commands2rst MODULE_PATH COMMAND_NAME

Extract docstrings from MODULE_PATH to create rst file named
COMMAND_NAME.rst for the program COMMAND_NAME

Arguments:

   MODULE_PATH:   The Python module path to the module to scan. eg: some.sub.module
   COMMAND_NAME:  The command line name of the program the documentation
                  is for

Options:

   -e, --email     author email
   -V, --version   software version
   -s, --program-description
                   one line program description
   -d, --description
                   full description
   -o, --organization
                   organization name
   -O, --options   options
   -a, --address   organization address
   -D, --date      date (defaults to current date if not specified)
   -c, --copyright
                   copyright
   -t, --rest      extra information to add
   -S, --synopsis  program synopsis
   -g, --group     man group (defaults to text processing)
   -i, --section   man page section number (defaults to 1)

  Plus all PROGRAM_OPTIONS (see `%(program)s --help')
"""

rst2man="""usage: %(program)s [PROGRAM_OPTIONS] man NAME

Convert a .rst file into a man page. If a directory called man1 exists in
the same directory as NAME, the man file is gzipped and put inside that
directory so you can test it by running this command in the current
working directory where COMMAND is the the the same as NAME without the
.rst extensions:

  man -M ./ COMMAND

Arguments:

   NAME:  The .rst file to convert to a man page

Options:

  All PROGRAM_OPTIONS (see `%(program)s --help')
"""

__program__="""usage: %(program)s [PROGRAM_OPTIONS] COMMAND [OPTIONS] ARGS

Commands (aliases):

   commands2help:  generate txt versions of the help text
   commands2rst:   create an rst file from the docstrings in a module
   rst2man:        generate a manpage from the generated rst file

Try `%(program)s COMMAND --help' for help on a specific command.
"""

