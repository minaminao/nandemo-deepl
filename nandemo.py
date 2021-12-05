import argparse
import json
import re
import string
from enum import Enum, auto
from pathlib import Path

import deepl
import docutils.parsers.rst
import docutils.utils

BASE_DIR_PATH = Path(__file__).parent
TRANSLATION_MEMO_FILEPATH = BASE_DIR_PATH / "translation_memo.json"


class State(Enum):
    PLAIN = auto()
    SKIP = auto()


def exp1(lines):
    parser = docutils.parsers.rst.Parser()

    components = (docutils.parsers.rst.Parser, )
    settings = docutils.frontend.OptionParser(components=components).get_default_values()

    document = docutils.utils.new_document('<rst-doc>', settings)

    parser.parse("\n".join(lines), document)

    print(type(document))
    for node in document:
        print(node[:5])


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("FILENAME", type=str, help="")
    parser.add_argument("--check", action="store_true", help="")
    parser.add_argument("-n", type=int, help="")
    parser.add_argument("-o", type=str, help="")
    args = parser.parse_args()

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
        if args.check:
            translated_text = "[" + text + "]"
        elif text in translation_memo:
            return translation_memo[text]
        else:
            translated_text = str(translator.translate_text(text, target_lang="JA"))
            translation_memo[text] = translated_text
        return translated_text

    def preprocess(text: str):
        S = string.ascii_uppercase.replace("A", "").replace("I", "")
        tmp = text[::]
        mapping = {}
        result = re.findall(r"(``[^`]+``|`[^`]+`_|:ref:`[^`]+`)", text)
        cnt = 0
        for x in result:
            if x in mapping:
                continue
            while True:
                t = S[cnt] * 2
                if t in tmp:
                    cnt += 1
                else:
                    break
            mapping[x] = t
            cnt += 1
            text = text.replace(x, mapping[x])
        return text, mapping

    def postprocess(text, mapping):
        if not args.check:
            for k, v in mapping.items():
                text = text.replace(v, " " + k + " ")
        return text

    blocks = Path(args.FILENAME).open().read().split("\n\n")

    state = State.PLAIN
    new_blocks = []

    if args.n:
        blocks = blocks[:args.n]

    for block in blocks:
        if block.startswith(".. code-block::") or block.startswith(".. _"):
            state = State.SKIP
            new_blocks.append(block)
            continue

        if state == State.SKIP:
            if block.startswith(" "):
                new_blocks.append(block)
                continue
            else:
                state = State.PLAIN

        if state == State.PLAIN:
            if block.startswith("**"):
                new_blocks.append(block)
            elif block.startswith(".. note::"):
                head, body = block.split("::\n", 1)
                text = " ".join([line.strip() for line in body.split("\n")])
                text, mapping = preprocess(text)
                text = translate(text)
                text = postprocess(text, mapping)
                new_block = head + "::\n" + text
                new_blocks.append(new_block)
            else:
                if "===" in block or "---" in block:
                    new_blocks.append(block)
                else:
                    bullet_list = False

                    text = block.replace("\n", " ")
                    text = re.sub(r"\s+", " ", text)
                    if text.startswith("* "):
                        bullet_list = True
                        text = text[2:]
                    text, mapping = preprocess(text)
                    text = translate(text)
                    text = postprocess(text, mapping)

                    new_block = ""
                    for x in block.split("\n"):
                        new_block += ".. " + x + "\n"
                    new_block += "\n"
                    if bullet_list:
                        new_block += "* " + text
                    else:
                        new_block += text
                    new_blocks.append(new_block)

    if args.o:
        Path(args.o).open("w").write("\n\n".join(new_blocks))
    else:
        Path("result.rst").open("w").write("\n\n".join(new_blocks))

    TRANSLATION_MEMO_FILEPATH.open("w").write(json.dumps(translation_memo))


if __name__ == "__main__":
    main()
