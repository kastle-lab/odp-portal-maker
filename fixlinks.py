#! /bin/python3

import argparse
import glob
import re
from os import path
from pathlib import Path

from progress.bar import Bar

from utils import read_file, resolve_path

#
# TODO: Fix how it process the links
# TODO: because somehow it it grabs the root dir of
# TODO: where the script is originated from
#


def fixlinks(ROOT_DIR='./out/'):
    """
        Fixes all the links including relative paths.
        It will ignore hyperlinks. The method will detect
        the directory depth and apply relativity accordingly
        to each links.

        Parameter:
        ROOT_DIR (str): Root directory. Defaults './out/'
    """
    ROOT_DIR = resolve_path(ROOT_DIR)

    files = glob.glob(
        '**/*.*',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    md_files = glob.glob(
        '**/*.md',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Fixing links...', max=len(md_files),
              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for filename in md_files:

        if path.isdir(ROOT_DIR + filename):
            bar.next()
            continue

        dir_depth = filename.replace('\\', '/').count('/')

        file_content = read_file(ROOT_DIR + filename)

        # To view how the regex works: https://regex101.com/r/oTWiTP/1
        # Essentially, it grabs the markdown link, then grabs only the link and
        # ignore everything else
        md_links = re.findall(r'(?<=\]\().*?(?=\s|\))', file_content, flags=re.MULTILINE)

        # To view regex: https://regex101.com/r/k572A6/1
        html_links = re.findall(r'(?<=href=\").+?(?=\")', file_content, flags=re.MULTILINE)

        # Make links into a set to remove duplicates
        for link in set([*md_links, *html_links]):

            # skip if hyperlink
            if ('http' in link):
                continue

            """ 1st Step - rewrite all the %253A to / """
            replacement_link = link.replace('.html', '')
            replacement_link = replacement_link.replace('%253A', '/')

            # This just makes sure the directory depth is reset just incase
            # maybe this program was ran before and the file location has
            # been moved
            replacement_link = replacement_link.replace('../', '')

            # Makes sure that the path string is normalized according to
            # the os being used
            replacement_link = path.normpath(replacement_link)

            """ 2nd Step - fix the relative paths after file directory cleaning """

            # Gets the only the filename
            tail = path.split(link)[1]
            parent_dir = path.split(filename)[0] or ROOT_DIR

            # Get the referenced file from the list of files after the cleaning
            # and it should give us the new path location
            # It will also try to resolve files using only it's filename
            # instead of trying to follow it's whole pathname
            r = re.compile(re.escape(f'{replacement_link}|{tail}$'))
            linked_file = list(filter(r.match, files))
            
            # If the link is not a file in our file list
            # then ignore it
            if len(linked_file) == 0:
                continue
            
            parent_regex = re.compile(re.escape('^' + parent_dir.replace('\\','/')))
            same_dir = list(filter(r.match, linked_file))

            # makes sure that
            # the path is absolute
            file_loc = resolve_path(ROOT_DIR + (same_dir or linked_file)[0])

            parent_dir = ROOT_DIR + parent_dir if parent_dir != ROOT_DIR else ROOT_DIR

            # Creates a relative path relative to where to original
            # markdown file is located
            # Adds a trailing ./ just incase it's in the same directory
            # and path.normpath will remove it if it is redundant
            replacement_link = path.normpath(path.relpath(file_loc, parent_dir))

            # the replace would only run on Windows filesystem, since
            # Windows uses the \ for directories
            replacement_link = replacement_link.replace('\\', '/')

            if not replacement_link.startswith('..'):
                replacement_link = './' + replacement_link

            file_content = file_content.replace(link, replacement_link)

        with open(ROOT_DIR + filename, 'w', encoding="utf-8") as write_file:
            write_file.write(file_content)

        bar.next()

    bar.finish()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(
        prog='Link Fixer',
        usage='fixlinks.py [-h help] input',
        description='Goes through every file in the directory and fixes the relative links',
        epilog='Part of the ODP-Portal-Maker toolset'
    )

    argParser.add_argument(
        'input',
        help='root directory of the files. Can be relative as long as the cwd is in the proper directory'
    )

    args = argParser.parse_args()
    root = args.input

    fixlinks(root)
