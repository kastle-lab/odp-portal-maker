import glob
from pathlib import Path
import os


def read_file(filename: str) -> str:
    """
        Reads the file as one big string and returns it.

        Parameters:
        filename (str): The filename to the file. Can be relative.
    """

    # Open file using the absolute path resolved by pathlib
    with open(resolve_path(filename), 'r', encoding='utf8') as file:
        lines = file.readlines()

        return ''.join(lines)


def resolve_path(path: str, directory: bool = False) -> str:
    """
        Ensures the path that was given
        can be consistent throughout the
        scripts, even if the given path
        is a relative one.

        If directory is True, then it will
        check for directories and if it
        doesn't exist, it will create one
    """
    p = Path(path)

    if directory and not p.is_dir():
        os.makedirs(p)

    # Add '/' for directories only
    return os.path.join(str(p.resolve()), '') if directory else str(p.resolve())


def cleanup_dir(root: str) -> None:
    """
        Globs through all folders in the given
        root folder, then sort it from the longest
        path to shortest (to delete from the inside 
        preventing folders still having another
        empty folder inside).
        Then it tries to remove it one by one,
        if the folder is not empty, then it will
        simply ignore it.
    """
    dirs = sorted(
        Path(root).glob('**'),
        key=lambda p: len(str(p)),
        reverse=True,
    )

    for directory in dirs:
        try:
            directory.rmdir()  # delete directory if it's empty
        except OSError:
            continue  # if it's not empty, then just ignore
