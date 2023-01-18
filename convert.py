# Libraries
import markdownify
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
    ROOT_DIR = resolve_path(ROOT_DIR, True)
    TARGET_DIR = resolve_path(TARGET_DIR, True)

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

                md = markdownify.markdownify(sanitized, heading_style='atx', strong_em_symbol=markdownify.UNDERSCORE)

                # https://regex101.com/r/UaNeFx/1
                md = re.sub('Retrieved from \"\[[\s\S]*\)', '', md, re.M)

                # https://regex101.com/r/TXBHRB/1
                md = re.sub('\[![\s\S]*Related submission, with evaluation history, can be found __here__', '', md, re.M)

                # https://regex101.com/r/njxznp/1
                md = re.sub('\[Add a reference\]\([\s\S]*\)', '', md, re.M)

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
        description='Converts html into markdown after sanitation',
        epilog='Part of ODP Portal Maker script'
    )

    argParser.add_argument(
        '-d',
        '-i',
        '--input',
        '--dir',
        help='root directory of the html files. Can be relative as long as the cwd is in the proper directory'
    )

    argParser.add_argument(
        '-o',
        '--output',
        help='output directory. Will also be used for directory cleaning and link fixing. If directory doesn\'t exist, it will create it'
    )

    args = argParser.parse_args()

    root = args.input
    out = args.output

    if not root:
        raise ValueError('Missing Argument: root directory')

    if not out:
        raise ValueError('Missing Argument: output directory')

    convert(root, out)
