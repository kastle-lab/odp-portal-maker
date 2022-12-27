# Libraries
import markdownify
import glob
from os import makedirs, path

# Modules
from sanitize import sanitize
from utils import read_file

# Literal path to the wiki leave empty if this file is in the wiki
ROOT_DIR = './example/'
TARGET_DIR = './md/'


def main():
    print('Scanning directory...')
    files = glob.glob(
        '**/*.html',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    for file in files:
        print(f'Reading {file}...')
        html = read_file(ROOT_DIR + file)

        print('Sanitizing file...')
        sanitized = sanitize(html)

        print('Converting...')
        md = markdownify.markdownify(sanitized, heading_style='atx', strong_em_symbol=markdownify.UNDERSCORE)

        # Creates directory recursively if it doesn't exist
        makedirs(path.dirname(TARGET_DIR + file), exist_ok=True)

        with open(TARGET_DIR + file.replace('.html', '.md'), 'w', encoding="utf8") as write_file:
            write_file.write(md.strip())


if __name__ == '__main__':
    main()
