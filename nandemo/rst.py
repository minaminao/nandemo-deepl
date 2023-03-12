import re
import string
from enum import Enum, auto
from pathlib import Path

import docutils.parsers.rst
import docutils.utils
from tqdm import tqdm

from .utils_deepl import translate


class State(Enum):
    PLAIN = auto()
    SKIP = auto()


def exp1(lines):
    """
    TODO: Use the docutils rst parser.
    """
    parser = docutils.parsers.rst.Parser()

    components = (docutils.parsers.rst.Parser, )
    settings = docutils.frontend.OptionParser(components=components).get_default_values()

    document = docutils.utils.new_document('<rst-doc>', settings)

    parser.parse("\n".join(lines), document)

    print(type(document))
    for node in document:
        print(node[:5])


def translate_rst(args, translator, translation_memo):
    def preprocess(text: str):
        ids = []
        S = string.ascii_uppercase
        for a in S:
            for b in S:
                ids.append(a + b)
        tmp = text[::]
        mapping = {}
        result = re.findall(r"(``[^`]+``|`[^`]+`_|:ref:`[^`]+`|`[^`]+`|\*\*[^\*]+\*\*)", text)
        cnt = 0
        for x in result:
            if x in mapping:
                continue
            while True:
                t = ids[cnt]
                if t in tmp:
                    cnt += 1
                else:
                    break
            mapping[x] = t
            cnt += 1
            text = text.replace(x, mapping[x])
        return text, mapping

    def postprocess(text: str, mapping):
        if not args.check:
            for k, v in mapping.items():
                text = text.replace(v, " " + k + " ")
        return text.strip()

    def get_indent(line):
        return len(line) - len(line.lstrip())

    raw_rst = Path(args.FILENAME).open().read()
    rst = raw_rst.replace(" note::", " note::\n").replace(" warning::", " warning::\n")
    blocks = re.split(r"\n\n+", rst)
    tmp_blocks = []
    for block in blocks:
        n_indent = get_indent(block)
        if block.strip().startswith("* "):
            lines = block.split("* ")
            for line in lines[1:]:
                tmp_blocks.append(" " * n_indent + "* " + line.strip())
        elif block.strip().startswith("- "):
            lines = block.split("- ")
            for line in lines[1:]:
                tmp_blocks.append(" " * n_indent + "- " + line.strip())
        elif block.strip().startswith("#. "):
            lines = block.split("#. ")
            for line in lines[1:]:
                tmp_blocks.append(" " * n_indent + "#. " + line.strip())
        elif block.strip().startswith("1. "):
            lines = re.split(r"\d\. ", block)
            for i, line in enumerate(lines[1:]):
                tmp_blocks.append(" " * n_indent + f"{i + 1}. " + line.strip())
        else:
            tmp_blocks.append(block)
    blocks = tmp_blocks

    state = State.PLAIN
    new_blocks = []

    buf = ""

    for block_i, block in tqdm(enumerate(blocks), total=len(blocks)):
        first_line = block.split("\n")[0].strip()

        if block.lstrip().startswith(".. code-block::") \
            or block.lstrip().startswith(".. _") \
            or block.lstrip().startswith(".. include::") \
            or block.lstrip().startswith(".. code::") \
            or block.lstrip().startswith(".. index::") \
            or block.lstrip().startswith(".. index:") \
            or block.lstrip().startswith(".. literalinclude::") \
            or (block.lstrip().startswith(".. ") and "::" not in first_line):

            state = State.SKIP
            new_blocks.append(block + "\n")
            continue

        if state == State.SKIP:
            if block.startswith(" "):
                new_blocks.append(block + "\n")
                continue
            else:
                state = State.PLAIN

        if state == State.PLAIN:
            if "***" in block or "###" in block or "===" in block or "---" in block or "~~~" in block or "^^^" in block:
                new_blocks.append(block + "\n")
            else:

                n_indent = get_indent(block)
                n_next_indent = get_indent(blocks[block_i + 1]) if block_i + 1 < len(blocks) else 0
                text = block.replace("\n", " ")
                # text = re.sub(r"\s+", " ", text)

                prefix = ""
                if text.startswith("* "):
                    prefix = "* "
                if text.startswith("- "):
                    prefix = "- "
                if text.startswith("#. "):
                    prefix = "#. "
                text = text[len(prefix):]

                text = text.strip()
                text, mapping = preprocess(text)
                if " note::" in text or " warning::" in text:
                    pass
                else:
                    text = translate(translator, text, translation_memo, args.check)
                text = postprocess(text, mapping)

                new_block = ""
                for x in block.split("\n"):
                    new_block += ".. " + x + "\n"

                if n_next_indent == 0:
                    new_block += "\n"

                buf += (" " * n_indent)
                buf += prefix + text + "\n\n"

                if n_next_indent == 0:
                    new_block += buf[:-1]
                    buf = ""

                new_blocks.append(new_block)
    
    return "\n".join(new_blocks)
