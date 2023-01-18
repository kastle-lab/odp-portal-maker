# Libraries
import re
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter, UNDERSCORE


# Modules
from utils import read_file


def sanitize(file: str) -> str:
    """
        Sanitizes the input by using regex to
        first query for the actual content
        then removing tables, scripts, and styles

        Parameters:
        file (str): the entire file read as a string
    """
    content = re.search(
        r"(<!--\s*?start\s*?content\s*?-->)[\s\S]+?(<!--\s*?end\s*?content\s*?-->)",
        file,
        flags=re.M | re.I
    )

    soup = BeautifulSoup(content.group(), 'html.parser')

    toc = soup.find('table', id='toc')

    # Remove all toc
    if toc:
        toc.decompose()

    # Remove all script tags
    for script in soup.find_all('script'):
        script.decompose()

    # Removes all inline styles
    for style in soup.find_all(style=True):
        del style['style']

    # Removes the footer
    footer = soup.select('div.printfooter')

    if footer:
        footer[0].decompose()

    catlinks = soup.find('div', id='catlinks')

    if catlinks:
        catlinks.decompose()

    # Remove that top table for certified patterns
    certified = soup.find('b', text=r'This pattern has been certified.')

    if certified:
        certified.parent.parent.decompose()

    ref = soup.find('a', text=r'Add a reference')

    if ref:
        ref.parent.decompose()

    # table_removed = re.sub(r'(<table.*?>)([\s\S]*?)(<\/table>)', '', file, flags=re.M | re.I)

    # scripts_removed = re.sub(r'(<script.*?>)([\s\S]*?)(<\/script>)', '', table_removed, flags=re.M | re.I)

    # cleaned = re.sub(r'(style=(\"|\')).+?(\"|\')', '', scripts_removed, flags=re.M | re.I)

    rebuild = f"""

<!DOCTYPE html>

<html>

    <body>

        {soup}

    </body>

</html>

    """

    return BeautifulSoup(rebuild, 'html.parser').prettify()
