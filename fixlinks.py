# Libraries
import re
import glob
from progress.bar import Bar
from os import path

# Modules
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
    ROOT_DIR = resolve_path(ROOT_DIR, True)

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
            dir_depth = filename.count('/') or filename.count('\\')

            file = read_file(ROOT_DIR + filename)

            # To view how the regex works: https://regex101.com/r/oTWiTP/1
            links = re.findall(r'(?<=\]\().*?(?=\s|\))', file, flags=re.MULTILINE)
            # Essentially, it grabs the markdown link, then grabs only the link and
            # ignore everything else

            for link in links:

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
                # then ignore it (most likely a hyperlink)
                if len(linked_file) == 0:
                    continue

                # the replace would only run on Windows filesystem, since
                # Windows uses the \ for directories
                replacement_link = ('../' * dir_depth) + linked_file[0].replace('\\', '/')
                replacement_link = replacement_link.replace('.md', '')

                file = file.replace(f'{link}', replacement_link)

            with open(ROOT_DIR + filename, 'w', encoding="utf-8") as write_file:
                write_file.write(file)

        bar.next()

    bar.finish()


if __name__ == '__main__':
    fixlinks('../odp-portal-test')
