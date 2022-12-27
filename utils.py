import glob
from pathlib import Path
from os import makedirs


def read_file(filename: str) -> str:
    """
        Reads the file as one big string and returns it.

        Parameters:
        filename (str): The filename to the file. Can be relative.
    """

    # Open file using the absolute path resolved by pathlib
    with open(Path(filename).resolve(), 'r', encoding='utf-8') as file:
        lines = file.readlines()

        return ''.join(lines)


def deep_dir_copy(src, target_root) -> list[str]:
    f"""
        Copies all directories inside the specified
        directory recursively.
        Note: It only copies the directories not files

        Returns:
        list[str]: The directories found by the method, in case needed
    """
    print('Scanning directories...')
    dirs = glob.glob(
        '*/**/',
        root_dir=src,
        recursive=True,
    )

    # print(dirs)

    print('Copying directories in target directory...')
    for directory in dirs:
        target = Path(target_root + directory).resolve()
        makedirs(target, exist_ok=True)

    return dirs
