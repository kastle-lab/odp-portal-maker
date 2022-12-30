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
