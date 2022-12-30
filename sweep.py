import glob
from os import unlink
from progress.bar import Bar

# Literal path to the wiki leave empty if this file is in the wiki
ROOT_DIR = './example/'


def main():
    clean_appledouble()

    clean_trash()

    print('Cleaned!')


# Cleans mostly unwanted redundant files
def clean_trash():
    files = glob.glob(
        '**/index.php*',
        root_dir=ROOT_DIR,
        recursive=True,
    )

    bar = Bar('Cleaning', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:

        try:
            unlink(ROOT_DIR + file)
            bar.next()

        except PermissionError:
            print('Permission denied')

        except:
            print('File can not be removed')


# Cleans the directory from ._ files (AppleDouble files)
def clean_appledouble():
    files = glob.glob(
        '**/._*',
        root_dir=ROOT_DIR,
        recursive=True,
        include_hidden=True
    )

    bar = Bar('Cleaning', max=len(files), suffix='%(percent).1f%% - [%(index)d of %(max)d] - %(eta)ds')

    for file in files:

        try:
            unlink(ROOT_DIR + file)
            bar.next()

        except PermissionError:
            print('Permission denied')

        except:
            print('File can not be removed')


if __name__ == '__main__':
    main()
