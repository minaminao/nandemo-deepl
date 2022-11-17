import argparse
import json
import os
from pathlib import Path

import deepl

from .md import translate_md
from .rst import translate_rst

BASE_DIR_PATH = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("FILENAME", type=str, help="")
    parser.add_argument("--check", action="store_true", help="")
    parser.add_argument("--check-plain", action="store_true", help="")
    parser.add_argument("-n", type=int, help="")
    parser.add_argument("-o", type=str, help="output file")
    parser.add_argument("--overwrite", action="store_true", help="")
    parser.add_argument("--filetype", choices=["rst", "md"], help="")
    args = parser.parse_args()

    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
    if not DEEPL_API_KEY:
        raise Exception("deepl_api_key.txt not found")
    translator = deepl.Translator(DEEPL_API_KEY)

    TRANSLATION_MEMO_FILEPATH = BASE_DIR_PATH / "translation_memo.json"
    translation_memo = json.load(TRANSLATION_MEMO_FILEPATH.open()) if TRANSLATION_MEMO_FILEPATH.exists() else {}

    if args.filetype == "rst":
        new_blocks = translate_rst(args, translator, translation_memo)
    elif args.filetype == "md":
        new_blocks = translate_md(args, translator, translation_memo)
    else:
        raise Exception("filetype not supported")

    TRANSLATION_MEMO_FILEPATH.open("w").write(json.dumps(translation_memo))


if __name__ == "__main__":
    main()
