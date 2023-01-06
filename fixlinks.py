# Libraries
import re
import glob
from progress.bar import Bar

# Modules
from utils import read_file, resolve_path


def fixlinks(ROOT_DIR='./out/'):
    files = glob.glob(
        '**/*.md',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Fixing links...', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for filename in files:
        file = read_file(ROOT_DIR + filename)

        # To view how the regex works: https://regex101.com/r/oTWiTP/1
        links = re.findall(r'(?<=\]\().*?(?=\s|\))', file, flags=re.MULTILINE)

        for link in links:

            replacement_link = link.replace('.html', '.md')
            replacement_link = replacement_link.replace('%253A', '/')

            file = file.replace(f'{link}', replacement_link)

        with open(resolve_path(ROOT_DIR + filename), 'w', encoding="utf-8") as write_file:
            write_file.write(file)
            bar.next()

    bar.finish()


if __name__ == '__main__':
    fixlinks()
