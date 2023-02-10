import argparse
import glob
import re
from os import path

from progress.bar import Bar

from utils import read_file, resolve_path


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

    bar = Bar('Fixing links...', max=len(files),
              suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for filename in files:

        if path.isdir(ROOT_DIR + filename):
            bar.next()
            continue

        if filename.endswith('.md'):
            dir_depth = filename.replace('\\', '/').count('/')
            # print(filename, dir_depth)

            file = read_file(ROOT_DIR + filename)

            # To view how the regex works: https://regex101.com/r/oTWiTP/1
            # Essentially, it grabs the markdown link, then grabs only the link and
            # ignore everything else
            md_links = re.findall(r'(?<=\]\().*?(?=\s|\))', file, flags=re.MULTILINE)

            # To view regex: https://regex101.com/r/k572A6/1
            html_links = re.findall(r'(?<=href=\").+?(?=\")', file, flags=re.MULTILINE)

            links = [*md_links, *html_links]

            # Make links into a set to remove duplicates
            for link in set(links):

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

                # Get the referenced file from the list of files after the cleaning
                # and it should give us the new path location
                linked_file = [x for x in files if replacement_link in x]

                # If the link is not a file in our file list
                # then ignore it
                if len(linked_file) == 0:
                    continue

                # the replace would only run on Windows filesystem, since
                # Windows uses the \ for directories
                replacement_link = ('../' * dir_depth) + linked_file[0].replace('\\', '/')
                replacement_link = replacement_link.replace('.md', '')

                file = file.replace(link, replacement_link)

            with open(ROOT_DIR + filename, 'w', encoding="utf-8") as write_file:
                write_file.write(file)

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
