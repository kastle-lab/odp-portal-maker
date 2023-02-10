import argparse
import glob
from os import makedirs, path, unlink
from pathlib import Path
from shutil import copy2, rmtree

from progress.bar import Bar

from utils import resolve_path


def move_module(ROOT_DIR, OUT_DIR, module, exclude_dir):
    # Makes sure these strings are a directory
    ROOT_DIR = resolve_path(ROOT_DIR)
    OUT_DIR = resolve_path(OUT_DIR)
    module = resolve_path(ROOT_DIR + module)

    if not path.exists(module):
        raise FileNotFoundError(f'Cannot find module {module}. Check the path.')

    files = glob.glob(
        '*.*' if exclude_dir else "**/*.*",
        recursive=True,
        root_dir=module,
    )

    # Progress Bar
    bar = Bar('Moving modules', max=len(files),
              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:
        # Make sure the parent folder of the file is created (ignored if exists)
        makedirs(OUT_DIR + str(Path(file).parent), exist_ok=True)

        # There are directories with a '.' in it's name
        # and this prevents any directories from being copied over
        if path.isdir(module + file):
            bar.next()
            continue

        # Copy files
        copy2(module + file, OUT_DIR + file)

        bar.next()

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Module Mover',
        usage='setup_page.py [-h help] [-f --force] [-x --exclude-dir] input module output',
        description='Moves specified module from converted html',
    )

    argParser.add_argument(
        'input',
        help='root directory of the converted markdown files (can be relative or absolute)',
    )

    argParser.add_argument(
        'module',
        help='module to move from root directory to output directory (not a path, should be the name of the folder inside the root)'
    )

    argParser.add_argument(
        'output',
        help='output path where the page is going to end up (can be relative or absolute)'
    )

    argParser.add_argument(
        '-x',
        '--exclude-dir',
        action='store_true',
        help='if flag is turned on, it will ignore all directories inside the input.'
    )

    argParser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='if flag is turned on, it will override everything in the output directory and if the directory doesn\'t exist, create one',
    )

    args = argParser.parse_args()

    root = args.input
    out = args.output
    module = args.module

    force = args.force
    exclude_dir = args.exclude_dir

    out = resolve_path(out)

    # If the '--force' flag is enabled, it will first
    # warn the user that it will override anything in
    # the target directory. It thens check if the
    # target dir exists, and deletes everything in it
    if force:
        print(
            '\n',
            'WARNING: Force flag is on. It will override the directory if it already exists.',
            sep=''
        )
        input('Press [Enter] to continue... or Terminate process to cancel')

        if path.exists(out):
            excludes = ['.git']

            folders = glob.glob(
                '**/',
                recursive=False,
                root_dir=out,
                include_hidden=False
            )

            for folder in folders:
                rmtree(out + folder)

            files = glob.glob(
                '*.*',
                recursive=False,
                root_dir=out
            )

            for file in files:
                unlink(out + file)

        makedirs(out, exist_ok=True)

    else:
        # No force mode
        try:
            # Will raise an exception if directory already exist
            makedirs(out)
        except FileExistsError as err:
            # Intercept and give hint to the --force flag
            raise FileExistsError(f'Directory already {out} exists. Use "--force" to overwrite')

    move_module(root, out, module)
