import re


def main():
    # Gets header
    file = read_file("Odp%3AAbout.html")

    header = re.search(r"(<head.*?>)([\s\S]*?)(<\/head>)", file, flags=re.M | re.I)

    header = clean_header(header.group())

    content = re.search(
        r"(<!--\s*?start\s*?content\s*?-->)[\s\S]+?(<!--\s*?end\s*?content\s*?-->)", file, flags=re.M | re.I)

    rebuild = f"""
<!DOCTYPE html>
<html>
    {header}
    <body>
        {content.group()}
    </body>
</html>
    """

    with open('Odp%3AAbout.html', 'w') as write_file:
        write_file.write(rebuild)


def clean_header(lines):

    scripts_removed = re.sub(r'(<script.*?>)([\s\S]*?)(<\/script>)', '', lines, flags=re.M | re.I)

    cleaned = re.sub(r'(style=(\"|\')).+?(\"|\')', '', scripts_removed, flags=re.M | re.I)

    return cleaned


def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        return ''.join(lines)


if __name__ == '__main__':
    main()


# Maybe useful later


# def remove_styles():
#     lines = read_file('ODPA.html')

#     cleaned = re.sub(r'(<style.*?>)([\s\S]*?)(<\/style>)', '', lines, flags=re.M | re.I)

#     with open('ODPA.html', 'w') as write_file:
#         write_file.write(cleaned)


# def remove_attr():
#     lines = read_file('ODPA.html')

#     id_removed = re.sub(r'(id=(\"|\')).+?(\"|\')', '', lines, flags=re.M | re.I)

#     class_removed = re.sub(r'(class=(\"|\')).+?(\"|\')', '', id_removed, flags=re.M | re.I)

#     style_removed = re.sub(r'(style=(\"|\')).+?(\"|\')', '', class_removed, flags=re.M | re.I)

#     with open('ODPA.html', 'w') as write_file:
#         write_file.write(style_removed)
