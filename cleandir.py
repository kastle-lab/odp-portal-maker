import glob
import re
from pathlib import Path
from os import makedirs, path, unlink, rename, getcwd
from shutil import copy2, copytree, rmtree
from utils import read_file, cleanup_dir
from progress.bar import Bar


def cleandir(ROOT_DIR='./md/', TARGET_DIR='./md/') -> None:
    """
        walks through all the directories,
        move them accordingly first, then it will find all the files
        and folders that has "%3A" in it's name, which is just a
        URL encoded string for ":" (colon), then creates it into a
        #folder and move the files and rename them accordingly. 
    """

    ROOT_DIR = str(Path(ROOT_DIR).resolve()) + '/'
    TARGET_DIR = str(Path(TARGET_DIR).resolve()) + '/'

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
            continue

        # Copy the file into the target
        copy2(orig_path, target_path)

        # Then delete the original file
        unlink(orig_path)

        cleanup_bar.next()

    cleanup_bar.finish()

    print('Cleaning up...')

    cleanup_dir(ROOT_DIR)

    print('Done!')


if __name__ == '__main__':
    cleandir()
