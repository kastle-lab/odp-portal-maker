# Libraries
import markdownify
import glob
from os import makedirs, path, unlink
from pathlib import Path

# Modules
from sanitize import sanitize
from utils import read_file, resolve_path, cleanup_dir
from progress.bar import Bar


def convert(ROOT_DIR='./example/', TARGET_DIR='./md/') -> None:
    """
        First it will use the sanitize module and 
        cleans up the html down to the actual content
        Then it converts the sanitized html into markdown
        and writes the file into the target directory

        Parameters:
        ROOT_DIR (str): Root directory path to the wiki
        TARGET_DIR (str): Output directory
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
        try:

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
        except FileNotFoundError:
            print('Cannot find file or', sep=' ')
            print('file has illegal character in name that results in the os not able to resolve the file:')
            print(file)
            print('Skipping...')
            continue

    bar.finish()


if __name__ == '__main__':
    convert()
