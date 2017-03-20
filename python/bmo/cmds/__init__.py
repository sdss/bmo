
import glob
import imp
import os

from .cmd_parser import bmo_parser


# This automatically imports every file in this directory so that the subparsrs
# are added to bmo_parser

cmd_files = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
for fn in cmd_files:

    mod_name = os.path.splitext(os.path.basename(fn))[0]
    if mod_name in ['__init__', 'cmd_parser']:
        continue

    imp.load_source(mod_name, fn)
