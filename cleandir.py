import argparse
import glob
import re
from os import getcwd, makedirs, path, rename, unlink
from pathlib import Path
from shutil import copy2, copytree, rmtree

from progress.bar import Bar

from utils import cleanup_dir, read_file, resolve_path


def cleandir(ROOT_DIR='./out/', TARGET_DIR=None) -> None:
    """
        walks through all the directories,
        move them accordingly first, then it will find all the files
        and folders that has "%3A" in it's name, which is just a
        URL encoded string for ":" (colon), then creates it into a
        #folder and move the files and rename them accordingly.
    """
    TARGET_DIR = ROOT_DIR if TARGET_DIR is None else TARGET_DIR

    ROOT_DIR = resolve_path(ROOT_DIR)
    TARGET_DIR = resolve_path(ROOT_DIR)

    paths = glob.glob(
        '**/*.*',
        root_dir=ROOT_DIR,
        recursive=True
    )

    cleanup_bar = Bar('Cleaning Directory',
                      max=len(paths),
                      suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds'
                      )

    for p in paths:
        # Literally replaces the ':' into a '/' that indicates a path
        cleaned_dir = p.replace('%3A', '/')

        orig_path = ROOT_DIR + p
        target_path = TARGET_DIR + cleaned_dir

        makedirs(path.dirname(target_path), exist_ok=True)

        # If it's a directory or it already exists, then ignore
        if path.isdir(orig_path) or path.exists(target_path):
            cleanup_bar.next()
            continue

        # Copy the file into the target
        copy2(orig_path, target_path)

        # Then delete the original file
        unlink(orig_path)

        cleanup_bar.next()

    cleanup_bar.finish()

    print('Cleaning up...')

    cleanup_dir(ROOT_DIR)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='Directory Cleaner',
        usage='cleandir.py [-h help] input [output]',
        description='Crawls throught the input directory and cleans it up. If output is not given, then it will clean it to the input directory',
        epilog='Part of the ODP-Portal-Maker toolset'
    )

    argParser.add_argument(
        'input',
        help='root directory of the files. Can be relative as long as the cwd is in the proper directory'
    )

    argParser.add_argument(
        'output',
        nargs='?',
        help='[optional] output directory to put the cleaned directory into. Can be relative. \nIf not provided, then it will use the input as the output',
        # default=argParser.parse_args().input
    )

    args = argParser.parse_args()
    root = args.input
    out = args.output or root

    cleandir(root, out)
