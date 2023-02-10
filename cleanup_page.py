
import argparse
import re
import glob
import json

from os import path, unlink, makedirs
from utils import read_file, resolve_path
from progress.spinner import Spinner
from progress.bar import Bar
from shutil import move
from setup_page import setup_config, setup_template


def cleanup_page(ROOT_DIR, remove_filters):
    ROOT_DIR = resolve_path(ROOT_DIR)

    if (not path.isdir(ROOT_DIR)):
        raise NotADirectoryError(f'{ROOT_DIR} is not a directory!')

    # filters = read_file(filter_file).split('\n')

    files = glob.glob(
        '**/*.*',
        recursive=True,
        root_dir=ROOT_DIR
    )

    spinner = Spinner('Cleaning Up Directory...')

    for pattern in remove_filters:
        compiled = re.compile(pattern)
        filtered = [f for f in files if compiled.match(f)]

        for filtered_file in filtered:
            unlink(resolve_path(ROOT_DIR + filtered_file))
            spinner.next()

    spinner.finish()

    print("Done!")


def organize_dir(ROOT_DIR, group_filters):
    ROOT_DIR = resolve_path(ROOT_DIR)

    if (not path.isdir(ROOT_DIR)):
        raise NotADirectoryError(f'{ROOT_DIR} is not a directory')

    files = glob.glob(
        '**/*.*',
        recursive=True,
        root_dir=ROOT_DIR
    )

    spinner = Spinner('Moving Grouped Files...')

    # filter out the grouped folders first
    for group in group_filters:
        dir_name = group['directory']
        regexes = group['regex']

        resolved_dir = resolve_path(ROOT_DIR + dir_name)

        # Create the directory according to the given name
        makedirs(resolved_dir, exist_ok=True)

        filtered = []

        for regex in regexes:
            pattern = re.compile(regex)
            filtered.extend([f for f in files if pattern.match(f)])

        for matching_file in filtered:
            # Move the file to respective directory
            move(resolve_path(ROOT_DIR + matching_file), resolve_path(resolved_dir + matching_file))

            # Avoid conflict by removing the moved file from the list of files
            files.remove(matching_file)

    bar = Bar('Organizing Files...', max=len(files),
              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:
        dir_name = resolve_path(ROOT_DIR + file.replace('.md', ''))

        makedirs(dir_name, exist_ok=True)

        move(resolve_path(ROOT_DIR + file), resolve_path(dir_name + file))
        bar.next()

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Page Cleanup Script',
        usage='setup_page.py [-h help] input filter',
        description='Cleans up the page outputted by setup. Using the filter as a regex to remove the files',
    )

    argParser.add_argument(
        'input',
        help='Input directory of the page to cleanup'
    )

    argParser.add_argument(
        'filter',
        nargs='*',
        default='filter.json',
        help='Filter file that will read line by line and use it as a regex to delete the files. Defaults to \'filter.json\''
    )

    args = argParser.parse_args()

    root = args.input
    filter_file = args.filter[0] if type(args.filter) is list else args.filter

    find_file = resolve_path(filter_file)

    filters = json.loads(read_file(filter_file))

    if (not path.exists(find_file)):
        raise FileNotFoundError(
            f'{filter_file} not found! Please create a filter.txt or give a valid path to a custom filter')

    cleanup_page(root, filters['remove'])
    organize_dir(root, filters['group'])
