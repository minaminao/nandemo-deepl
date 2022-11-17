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
    parser.add_argument("--output", type=str, help="output file")
    parser.add_argument("--overwrite", action="store_true", help="")
    parser.add_argument("--filetype", choices=["rst", "md"], help="")
    parser.add_argument("--ast", action="store_true", help="")
    args = parser.parse_args()

    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
    if not DEEPL_API_KEY:
        raise Exception("$DEEPL_API_KEY is not set")
    translator = deepl.Translator(DEEPL_API_KEY)

    TRANSLATION_MEMO_FILEPATH = BASE_DIR_PATH / "translation_memo.json"
    translation_memo = json.load(TRANSLATION_MEMO_FILEPATH.open()) if TRANSLATION_MEMO_FILEPATH.exists() else {}

    filetype = args.FILENAME.split(".")[-1] if args.filetype is None else args.filetype

    match filetype:
        case "rst":
            result = translate_rst(args, translator, translation_memo)
        case "md":
            result = translate_md(args, translator, translation_memo)
        case "_":
            raise Exception("filetype not supported")

    TRANSLATION_MEMO_FILEPATH.open("w").write(json.dumps(translation_memo))

    if args.output:
        Path(args.output).open("w").write(result)
    elif args.overwrite:
        Path(args.FILENAME).open("w").write(result)
    else:
        print(result)


if __name__ == "__main__":
    main()
