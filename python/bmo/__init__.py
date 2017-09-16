
import warnings

warnings.filterwarnings(
    'ignore', 'Matplotlib is building the font cache using fc-list. This may take a moment.')


# BMO uses pathlib2 in python 2, in preparation to become PY3-only.
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
