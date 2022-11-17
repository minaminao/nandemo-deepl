import json
from pathlib import Path

from mistletoe import Document, ast_renderer

from .utils_deepl import *


def translate_md(args, translator, translation_memo):
    file = Path(args.FILENAME).open("r")
    doc = Document(file)
    ast = ast_renderer.get_ast(doc)
    print(ast)
    print(json.dumps(ast))
