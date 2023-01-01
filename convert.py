# Libraries
import markdownify
import glob
from os import makedirs, path, unlink
from pathlib import Path

# Modules
from sanitize import sanitize
from utils import read_file, resolve_path, cleanup_dir
from progress.bar import Bar


def convert(ROOT_DIR='./example/', TARGET_DIR='./md/', cleanup=False) -> None:
    """
        First it will use the sanitize module and 
        cleans up the html down to the actual content
        Then it converts the sanitized html into markdown
        and writes the file into the target directory

        It is recommended if the target directory is 
        going to be in a different parent directory, that
        the cleanup flag be False.

        If the target directory is going to be the
        same directory, the cleanup flag should be 
        turned to True to avoid a messy directory

        Parameters:
        ROOT_DIR (str): Root directory path to the wiki
        TARGET_DIR (str): Output directory
        cleanup (bool): True if the source directory is to be cleaned up and deleted after conversion is done
                        False if the source directory is to be left behind
    """
    ROOT_DIR = str(Path(ROOT_DIR).resolve()) + '/'
    TARGET_DIR = str(Path(TARGET_DIR).resolve()) + '/'

    print('Scanning directory...')
    files = glob.glob(
        '**/*.html',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Converting', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for idx, file in enumerate(files):
        html = read_file(ROOT_DIR + file)

        # print('Sanitizing file...')
        sanitized = sanitize(html)

        # print('Converting...')
        md = markdownify.markdownify(sanitized, heading_style='atx', strong_em_symbol=markdownify.UNDERSCORE)

        # Creates directory recursively if it doesn't exist
        makedirs(path.dirname(TARGET_DIR + file), exist_ok=True)

        # Write file into target directory and write it as markdown
        with open(TARGET_DIR + file.replace('.html', '.md'), 'w', encoding="utf8") as write_file:
            write_file.write(md.strip())

        bar.next()

    bar.finish()

    if cleanup:
        print('Cleanup flag enabled...')
        cleanup_src(ROOT_DIR)


def cleanup_src(root):
    html_files = glob.glob(
        '**/*.html',
        root_dir=root,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Cleanup source', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in html_files:
        unlink(resolve_path(root + file))
        bar.next()

    bar.finish()

    cleanup_dir(root)


if __name__ == '__main__':
    convert()
