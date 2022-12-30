# Libraries
import re

# Modules
from utils import read_file


def sanitize(file):
    """
        Sanitizes the input by using regex to
        first query for the actual content
        then removing tables, scripts, and styles

        Parameters:
        file (str): the entire file read as a string
    """

    table_removed = re.sub(r'(<table.*?>)([\s\S]*?)(<\/table>)', '', file, flags=re.M | re.I)

    scripts_removed = re.sub(r'(<script.*?>)([\s\S]*?)(<\/script>)', '', table_removed, flags=re.M | re.I)

    cleaned = re.sub(r'(style=(\"|\')).+?(\"|\')', '', scripts_removed, flags=re.M | re.I)

    content = re.search(

        r"(<!--\s*?start\s*?content\s*?-->)[\s\S]+?(<!--\s*?end\s*?content\s*?-->)", cleaned, flags=re.M | re.I)

    rebuild = f"""

<!DOCTYPE html>

<html>

    <body>

        {content.group()}

    </body>

</html>

    """

    return rebuild
