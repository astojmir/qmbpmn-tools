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
# Code author:  Aleksandar Stojmirovic
#

"""Distutils based setup script for qmbpmn package.

This uses Distutils (http://python.org/sigs/distutils-sig/) the standard
python mechanism for installing packages. For the easiest installation
just type the command:

python setup.py install
"""

from distutils.core import setup, Extension
from version import CURRENT_VERSION

PACKAGES = [
    'qmbpmn',
    'qmbpmn.ITMProbe',
    'qmbpmn.ITMProbe.core',
    'qmbpmn.common',
    'qmbpmn.common.commandtool',
    'qmbpmn.common.db_parsers',
    'qmbpmn.common.graph',
    'qmbpmn.common.graphics',
    'qmbpmn.common.utils',
    'qmbpmn.common.pkg',
    'qmbpmn.web',
    'qmbpmn.web.SaddleSum',
    'qmbpmn.web.ITMProbe',
    ]

SCRIPTS = ['scripts/qmbpmn-datasets',
           'scripts/qmbpmn-deploy',
           'scripts/qmbpmn-server',
           'scripts/qmbpmn-clean-temp',
           'scripts/itmprobe',
           ]

PACKAGE_DATA = {'qmbpmn.ITMProbe': ['doc/Makefile',
                                    'doc/source/*',
                                    'itm_scripts/*',
                                    ],
                'qmbpmn.common.graphics': ['ColorBrewer.txt'],
                'qmbpmn.web': ['static/*',
                               'netmap/*',
                               'config/*',
                               'templates/*.*',
                               'templates/ITMProbe/*',
                               'templates/enrich/*'],
                }

setup(
    name='qmbpmn-tools',
    version=CURRENT_VERSION,
    author='Aleksandar Stojmirovic and Yi-Kuo Yu',
    author_email='stojmira@ncbi.nlm.nih.gov',
    url='http://www.ncbi.nlm.nih.gov/CBBresearch/Yu/',
    package_dir={'qmbpmn': '.'},
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    scripts=SCRIPTS,
    description='Code from QMBP group for modelling information flow in networks.',
    license='Public Domain',
    platforms='POSIX',
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
    )
