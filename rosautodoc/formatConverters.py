# Set of valid doc formats
MARKDOWN = "markdown"
HTML = "html"

# List of supported documentation formats
SUPPORTED_DOC_FORMATS = [
    MARKDOWN,
    HTML,
]


class FileExtension:
    """The FileExtension class makes it possible to get the file extension
    based on the format of the file.

    """

    @classmethod
    def get(cls, docFormat):
        """Return the file extension string (e.g., "html") for the
        desired documentation format.

        * docFormat -- the documentation format identifier

        """
        extensionMap = {
            MARKDOWN: "md",
            HTML: "html",
        }

        return extensionMap.get(docFormat)


class MarkdownToHtml:
    """The MarkdownToHtml class deals with converting markdown content
    to HTML content.

    """

    @classmethod
    def convert(cls, lines):
        """Conver the given markdown data (as a list of strings) into HTML
        content (also as a list of strings).

        * lines -- the input list of markdown lines

        """
        htmlLines = [
            "<html>",
            "<head>"
            "</head>",
        ]

        writingList = False
        for line in lines:
            isList = False
            if line.startswith("## "):
                # Subsection
                data = line[3:]
                line = "<h2>%s</h2>" % data
            elif line.startswith("# "):
                # Section
                data = line[2:]
                line = "<h1>%s</h1>" % data
            elif line.startswith("- "):
                # List entry
                isList = True
                if not writingList:
                    htmlLines.append("<ul>")
                    writingList = True

                data = line[2:]
                line = "<li>%s</li>" % data
            elif len(line.strip()) > 0:
                # Normal text content
                line = "<p>%s</p>" % line

            # Close a list that has ended
            if not isList and writingList:
                htmlLines.append("</ul>")
                writingList = False

            htmlLines.append(line)

        # Close the list if one was being created
        if writingList:
            htmlLines.append("</ul>")

        htmlLines.extend([
            "</html>",
        ])

        return htmlLines
