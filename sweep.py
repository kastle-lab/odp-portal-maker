import argparse
import glob
from os import unlink

from progress.bar import Bar

from utils import resolve_path


# Cleans mostly unwanted redundant files
def clean_trash(ROOT_DIR):
    files = glob.glob(
        '**/index.php*',
        root_dir=ROOT_DIR,
        recursive=True,
    )

    bar = Bar('Cleaning', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:
        try:
            unlink(ROOT_DIR + file)
            bar.next()

        except PermissionError:
            print('Permission denied')

        except:
            print('File can not be removed')

    bar.finish()


# Cleans the directory from ._ files (AppleDouble files)
def clean_appledouble(ROOT_DIR):
    files = glob.glob(
        '**/._*',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Cleaning', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:

        try:
            unlink(ROOT_DIR + file)
            bar.next()

        except PermissionError:
            print('Permission denied')

        except:
            print('File can not be removed')

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='Directory Sweeper',
        usage='sweep.py [-h help] input',
        description='Goes through the directory specified and removes all "._" files and index.php* files',
        epilog='Part of the ODP-Portal-Maker toolset'

    )

    argParser.add_argument(
        'input',
        help='path to directory to sweep',
    )

    args = argParser.parse_args()

    root = args.input

    ROOT_DIR = resolve_path(root)

    clean_appledouble(ROOT_DIR)

    clean_trash(ROOT_DIR)
