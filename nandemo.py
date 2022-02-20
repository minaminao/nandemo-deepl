import argparse
import json
import re
import string
from enum import Enum, auto
from pathlib import Path
from tqdm import tqdm

import deepl
import docutils.parsers.rst
import docutils.utils
from mistletoe import Document, ast_renderer 

BASE_DIR_PATH = Path(__file__).parent
TRANSLATION_MEMO_FILEPATH = BASE_DIR_PATH / "translation_memo.json"


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

deepl_api_key_filepath = BASE_DIR_PATH / "deepl_api_key.txt"
if deepl_api_key_filepath.exists():
    deepl_api_key = deepl_api_key_filepath.open().read().strip()
    translator = deepl.Translator(deepl_api_key)
else:
    raise Exception("deepl_api_key.txt not found")

if TRANSLATION_MEMO_FILEPATH.exists():
    translation_memo = json.load(TRANSLATION_MEMO_FILEPATH.open())
else:
    translation_memo = {}


def translate(text):
    global args
    if text == "":
        translated_text = ""
    elif args.check:
        translated_text = "[" + text + "]"
    elif args.check_plain:
        translated_text = text
    elif text in translation_memo:
        translated_text = translation_memo[text]
    else:
        translated_text = str(translator.translate_text(text, target_lang="JA"))
        translation_memo[text] = translated_text
    return translated_text


def translate_rst():
    global args

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
            ls = block.split("* ")
            for l in ls[1:]:
                tmp_blocks.append(" " * n_indent + "* " + l.strip())
        elif block.strip().startswith("- "):
            ls = block.split("- ")
            for l in ls[1:]:
                tmp_blocks.append(" " * n_indent + "- " + l.strip())
        elif block.strip().startswith("#. "):
            ls = block.split("#. ")
            for l in ls[1:]:
                tmp_blocks.append(" " * n_indent + "#. " + l.strip())
        elif block.strip().startswith("1. "):
            ls = re.split(r"\d\. ", block)
            for i, l in enumerate(ls[1:]):
                tmp_blocks.append(" " * n_indent + f"{i + 1}. " + l.strip())
        else:
            tmp_blocks.append(block)
    blocks = tmp_blocks

    state = State.PLAIN
    new_blocks = []

    if args.n:
        blocks = blocks[:args.n]

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
                    text = translate(text)
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

    if args.o:
        Path(args.o).open("w").write("\n".join(new_blocks))
    elif args.overwrite:
        Path(args.FILENAME).open("w").write("\n".join(new_blocks))
    else:
        Path("result.rst").open("w").write("\n".join(new_blocks))


def translate_md():
    global args

    file = Path(args.FILENAME).open("r")
    doc = Document(file)
    ast = ast_renderer.get_ast(doc)
    print(json.dumps(ast))


def main():
    global args

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("FILENAME", type=str, help="")
    parser.add_argument("--check", action="store_true", help="")
    parser.add_argument("--check_plain", action="store_true", help="")
    parser.add_argument("-n", type=int, help="")
    parser.add_argument("-o", type=str, help="output file")
    parser.add_argument("--overwrite", action="store_true", help="")
    parser.add_argument("--filetype", choices=["rst", "md"], help="")
    args = parser.parse_args()

    if args.filetype == "rst":
        new_blocks = translate_rst()
    elif args.filetype == "md":
        new_blocks = translate_md()
    else:
        raise Exception("filetype not supported")

    TRANSLATION_MEMO_FILEPATH.open("w").write(json.dumps(translation_memo))


if __name__ == "__main__":
    main()
