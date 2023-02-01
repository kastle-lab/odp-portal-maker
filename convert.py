# Libraries
from markdownify import MarkdownConverter, UNDERSCORE
import glob
import re
import argparse
from os import makedirs, path, unlink
from pathlib import Path
from shutil import copy2

# Modules
from sanitize import sanitize
from utils import read_file, resolve_path, cleanup_dir
from progress.bar import Bar


# The purpose of this class is so that when
# a list inside a table is being converted
# it will just keep it as the html
class CustomConverter(MarkdownConverter):

    def convert_li(self, el, text, convert_as_inline):
        if el.parent.parent.name == 'td':
            return str(el)
        else:
            return super().convert_li(el, text, convert_as_inline).replace('\n', '')

    # These two will keep the table rows into one line to avoid ugly looking tables
    def convert_td(self, el, text, convert_as_inline):
        return ' ' + text.replace('\n', '') + ' |'

    def convert_th(self, el, text, convert_as_inline):
        return ' ' + text.replace('\n', '') + ' |'


def markdownify(html, **options):
    return CustomConverter(**options).convert(html)


def convert(ROOT_DIR, TARGET_DIR) -> None:
    """
        First it will use the sanitize module and
        cleans up the html down to the actual content
        Then it converts the sanitized html into markdown
        and writes the file into the target directory

        Parameters:
        ROOT_DIR (str): Root directory path to the wiki
        TARGET_DIR (str): Output directory
    """
    ROOT_DIR = resolve_path(ROOT_DIR)
    if (not path.isdir(resolve_path(TARGET_DIR))):
        makedirs(resolve_path(TARGET_DIR) + '/')
    TARGET_DIR = resolve_path(TARGET_DIR)

    print('Scanning directory...')
    files = glob.glob(
        '**/*.*',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Converting', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for idx, file in enumerate(files):

        # If it's not an html file, don't convert it just move it
        if not file.endswith('.html'):

            orig_path = ROOT_DIR + file
            target_path = TARGET_DIR + file

            # Creates directory recursively if it doesn't exist
            makedirs(path.dirname(TARGET_DIR + file), exist_ok=True)

            if not (path.isdir(orig_path) or path.exists(target_path)):
                # Copy the file into the target
                copy2(orig_path, target_path)

            bar.next()

        else:
            try:

                html = read_file(ROOT_DIR + file)

                sanitized = sanitize(html)

                md = markdownify(sanitized, heading_style='atx', strong_em_symbol=UNDERSCORE)

                # Creates directory recursively if it doesn't exist
                makedirs(path.dirname(TARGET_DIR + file), exist_ok=True)

                # Write file into target directory and write it as markdown
                with open(TARGET_DIR + file.replace('.html', '.md'), 'w', encoding="utf-8") as write_file:
                    write_file.write(md.strip())
                bar.next()

            except FileNotFoundError:
                print('\nCannot find file or', end=' ')
                print('file has illegal character in name that results in the os not able to resolve the file:')
                print(file)
                print('Skipping...')
                bar.next()
                continue

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='File Converter',
        usage='convert.py [-h help] input output',
        description='Converts html into markdown after sanitation',
        epilog='Part of the ODP-Portal-Maker toolset'
    )

    argParser.add_argument(
        'input',
        help='root directory of the html files. Can be relative as long as the cwd is in the proper directory'
    )

    argParser.add_argument(
        'output',
        help='output directory. Will also be used for directory cleaning and link fixing. If directory doesn\'t exist, it will create it'
    )

    args = argParser.parse_args()

    root = args.input
    out = args.output

    convert(root, out)
