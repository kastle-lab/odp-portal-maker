import markdownify
import glob
from sanitize import sanitize
from os import makedirs, path

# Literal path to the wiki leave empty if this file is in the wiki
ROOT_DIR = 'C:/Users/Gilbert/Codes/wiki/'
TARGET_DIR = 'C:/Users/Gilbert/Codes/md/'


def read_file(filename):
    with open(filename, 'r', encoding="utf8") as file:
        lines = file.readlines()
        return ''.join(lines)


def main():
    print('Reading directory...')
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

        makedirs(path.dirname(TARGET_DIR + file), exist_ok=True)
        with open(TARGET_DIR + file.replace('.html', '.md'), 'w', encoding="utf8") as write_file:
            write_file.write(md.strip())


if __name__ == '__main__':
    main()
