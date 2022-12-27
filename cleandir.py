import glob
import re
from pathlib import Path
from os import makedirs, path, unlink, rename, rmdir, getcwd
from shutil import copy2, copytree
from utils import read_file, deep_dir_copy
from urllib.parse import unquote

ROOT_DIR = './md/'
TARGET_DIR = './md/'

# Essentially, this script will walk through all the directories,
# move them accordingly first, then it will find all the files
# and folders that has "%3A" in it's name, which is just a
# URL encoded string for ":" (colon), then creates it into a
# folder and move the files and rename them accordingly.


def main():

    paths = glob.glob(
        '**/*.*',
        root_dir=ROOT_DIR,
        recursive=True
    )

    for p in paths:
        decoded = unquote(p)

        cleaned_dir = decoded.replace(':', '/')

        orig_path = ROOT_DIR + p
        target_path = TARGET_DIR + cleaned_dir

        makedirs(path.dirname(target_path), exist_ok=True)

        print(f'Copying {p}')
        copy2(orig_path, target_path)

        print('Deleting original...')
        unlink(orig_path)

    print('Cleaning up...')
    # Remove old directories
    # Running in reverse to delete from the inside out.
    for directory in reversed(paths):
        old_dir = path.dirname(ROOT_DIR + directory)

        # If the path is already deleted, then skip
        if not path.exists(old_dir):
            continue

        # Make sure it's not the root directory itself being removed
        # and make sure that it's not the current directory the script
        # is running from. rmdir should error out if directory is not empty
        # but just to be sure
        if not path.samefile(old_dir, ROOT_DIR) and not path.samefile(old_dir, getcwd()):
            rmdir(old_dir)

    print('Done!')


def move_files():

    deep_dir_copy(ROOT_DIR, TARGET_DIR)

    print('Scanning files...')
    files = glob.glob(
        '**/*.html',
        root_dir=ROOT_DIR,
        recursive=True
    )

    for file in files:
        source = Path(ROOT_DIR + file).resolve()
        target = Path(TARGET_DIR + file).resolve()

        print(f'Copying {file}')
        copy2(source, target)


if __name__ == '__main__':
    main()
