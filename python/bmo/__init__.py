
# BMO uses pathlib2 in python 2, in preparation to become PY3-only.
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

import yaml

# Monkeypatches formatwarning

import warnings


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    basename = pathlib.Path(filename).name
    return '[{}]: {} ({}:{})'.format(category.__name__, message, basename, lineno)


warnings.formatwarning = warning_on_one_line

warnings.filterwarnings(
    'ignore', 'Matplotlib is building the font cache using fc-list. This may take a moment.')


config = yaml.load(open(str(pathlib.Path(__file__).parents[2] / 'etc/bmo.cfg')))


__version__ = '0.2.0dev'
