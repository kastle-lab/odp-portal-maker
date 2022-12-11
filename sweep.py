# Cleans the directory from ._ files (AppleDouble files)
import glob
from os import unlink

# Literal path to the wiki leave empty if this file is in the wiki
PATH_TO_WIKI = ""


def main():
    files = glob.glob(
        "**/._*",
        root_dir=PATH_TO_WIKI,
        recursive=True,
        include_hidden=True
    )

    for file in files:
        print(f"Deleting: {file}")

        try:
            unlink(PATH_TO_WIKI + file)
            print(f"Deleted: {file}")

        except PermissionError:
            print("Permission denied")

        except:
            print("File can not be removed")

if __name__ == "__main__":
    main()
