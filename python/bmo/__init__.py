
# BMO uses pathlib2 in python 2, in preparation to become python3-only.
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

import yaml


# Monkeypatches formatwarning and error handling

import click
import warnings


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):

    basename = pathlib.Path(filename).name
    category_colour = click.style('[{}]'.format(category.__name__), fg='yellow')

    return '{}: {} ({}:{})\n'.format(category_colour, message, basename, lineno)


warnings.formatwarning = warning_on_one_line

warnings.filterwarnings(
    'ignore', 'Matplotlib is building the font cache using fc-list. This may take a moment.')


# Loads config
config = yaml.load(open(str(pathlib.Path(__file__).parent / 'etc/bmo.cfg')))


__version__ = '0.2.0dev'
