#!/usr/bin/python3

"""Function with md5 converter and c_remover"""

if __name__ == "__main__":
    import os
    import sys
    import hashlib

    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        exit(1)

    if not os.path.exists(sys.argv[1]):
        sys.stderr.write("Missing " + sys.argv[1] + "\n")
        exit(1)

    with open(sys.argv[1], "r") as f_mark:
        lines = f_mark.readlines()

    # <em> & <b> & md5 & c_remover
    def inline_modifier(txt_content):
        def content_isolater(symbol):
            start = txt_content.find(symbol)
            end = txt_content.find(symbol, start + 2)

            # Last Cases are specials:
            if symbol == "[[":
                end = txt_content.find("]]", start + 2)
            if symbol == "((":
                end = txt_content.find("))", start + 2)

            if end == -1:
                raise ValueError("Closing symbol not found")
            symbol_content = txt_content[start + 2 : end]
            return symbol_content

        while "**" in txt_content:
            try:
                b = content_isolater("**")
                txt_content = txt_content.replace(f"**{b}**", f"<b>{b}</b>", 1)
            except ValueError:
                break

        while "__" in txt_content:
            try:
                em = content_isolater("__")
                txt_content = txt_content.replace(f"__{em}__", f"<em>{em}</em>", 1)
            except ValueError:
                break

        while "[[" in txt_content:
            try:
                hashed_text = content_isolater("[[")
                txt_content = txt_content.replace(
                    f"[[{hashed_text}]]", convert_hash(hashed_text), 1
                )
            except ValueError:
                break

        while "((" in txt_content:
            try:
                c_txt = content_isolater("((")
                txt_content = txt_content.replace(
                    f"(({c_txt}))", c_remover(c_txt, "c"), 1
                )
            except ValueError:
                break

        return txt_content

    def convert_hash(text):
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode("utf-8"))
        md5 = md5_hash.hexdigest()
        return md5

    def c_remover(text, letter):
        text = text.replace(letter.lower(), "")
        text = text.replace(letter.upper(), "")
        return text

    def convert_markdown(line):
        html_line = ""
        if line.startswith("#"):
            h_level = line.count("#")
            txt_content = line[h_level:].strip()
            html_line += f"<h{h_level}>{inline_modifier(txt_content)}</h{h_level}>"

        elif line.startswith("**") and line.endswith("**"):
            txt_content = line[2:-2].strip()
            html_line += f"<p>\n<b>{inline_modifier(txt_content)}</b>\n</p>"

        elif line.startswith("-") or line.startswith("*"):
            txt_content = line[1:].strip()
            html_line += f"<li>{inline_modifier(txt_content)}</li>"

        # elif line.startswith("*") and line[1] != "*" and not line.endswith("**"):
        #     txt_content = line[1:].strip()
        #     html_line += f"<li>{inline_modifier(txt_content)}</li>"

        elif line != "":
            html_line += inline_modifier(line)

        return html_line

    html_content = []
    previous_line = ""
    in_paragraph = False
    paragraph_lines = []

    for line in lines:
        line = line.strip()
        if (
            line.startswith("*")
            and not line.startswith("**")
            and not previous_line.startswith("*")
        ):
            html_content.append("<ol>")
        if line.startswith("-") and not previous_line.startswith("-"):
            html_content.append("<ul>")

        if not line.startswith("*") and previous_line.startswith("*"):
            html_content.append("</ol>")
        if not line.startswith("-") and previous_line.startswith("-"):
            html_content.append("</ul>")

        if line == "" and in_paragraph:
            html_content.append("<p>")
            html_content.append("\n<br/>\n".join(paragraph_lines))
            html_content.append("</p>")
            paragraph_lines = []
            in_paragraph = False

        if line != "" and not line.startswith(("#", "-", "*")):
            paragraph_lines.append(convert_markdown(line))
            in_paragraph = True

        else:
            html_content.append(convert_markdown(line))

        previous_line = line

    if previous_line.startswith("-"):
        html_content.append("</ul>")
    if previous_line.startswith("*") and not previous_line.startswith("**"):
        html_content.append("</ol>")

    # Allowing the last line to be appended
    if in_paragraph:
        html_content.append("<p>")
        html_content.append("<br/>\n".join(paragraph_lines))
        html_content.append("</p>")

    html_version = "\n".join(html_content)

    with open(sys.argv[2], "w") as f_html:
        f_html.write(html_version)

    exit(0)