import argparse
import glob
import re
from os import makedirs, path
from pathlib import Path
from shutil import copy2

from progress.bar import Bar

from utils import read_file, resolve_path


def import_required_files(ROOT_DIR, SRC_DIR):
    ROOT_DIR = resolve_path(ROOT_DIR)
    SRC_DIR = resolve_path(SRC_DIR)

    # Gets every file
    files = glob.glob(
        '**/*.*',
        recursive=True,
        root_dir=SRC_DIR
    )

    # Ignore any files that is not a markdown
    files = [f for f in files if not f.endswith('.md')]

    out_files = glob.glob(
        '**/*.md',
        recursive=True,
        root_dir=ROOT_DIR
    )

    bar = Bar('Importing necessary files', max=len(out_files),
              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for filename in out_files:
        if path.isdir(filename):
            bar.next()
            continue

        file_content = read_file(ROOT_DIR + filename)

        # Grabs all markdown links
        # To view how the regex works: https://regex101.com/r/oTWiTP/1
        md_links = re.findall(r'(?<=\]\().*?(?=\s|\))', file_content, flags=re.MULTILINE)

        # To view regex: https://regex101.com/r/k572A6/1
        html_links = re.findall(r'(?<=href=\").+?(?=\")', file_content, flags=re.MULTILINE)

        links = [*md_links, *html_links]

        # print()

        for link in links:
            # https://regex101.com/r/vk2ZEy/1
            if link.endswith('.md') or not re.search(r'\.[\w]*$', link):
                continue

            req_file = link.replace('../', '')

            # normalize the path
            req_file = path.normpath(req_file)

            orig_loc = resolve_path(SRC_DIR + req_file)

            # This will get us only the filename, and throws away the
            # unecessary paths
            _, tail = path.split(req_file)

            new_loc = resolve_path(ROOT_DIR + f'{Path(filename).parent}/{tail}')

            # If file doesn't exist in the original directory
            # (which means it's a url) or the path is a directory
            # then skip over
            if not path.exists(orig_loc) or path.isdir(orig_loc):
                continue

            # makedirs(OUT_DIR + str(Path(req_file).parent), exist_ok=True)

            copy2(orig_loc, new_loc)

        bar.next()

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='ODP Portal Module Mover',
        usage='resolve_imports.py [-h help] directory source',
        description='Moves files linked by the markdown files',
    )

    argParser.add_argument(
        'directory',
        help='directory to scan linked files and move to',
    )

    argParser.add_argument(
        'source',
        help='source path where to look for files to import'
    )

    args = argParser.parse_args()

    root = args.directory
    source = args.source

    import_required_files(root, source)
