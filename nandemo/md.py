import json
import re
from pathlib import Path

from mistletoe import Document, ast_renderer

from .utils_deepl import *

html_pattern = re.compile(r"(<(\".*?\"|'.*?'|[^'\"])*?>)+", re.MULTILINE | re.DOTALL)

def get_constant_id(mapping):
    return "X" + str(len(mapping)).zfill(2)

def node_to_text(node, list_depth=0, translator=None, mapping=None, translation_memo=None) -> str:
    text = ""
    match node["type"]:
        case "Document":
            text += "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
        case "Heading":
            assert len(node["children"]) == 1
            text += ("#" * node["level"]) + " " + node_to_text(node["children"][0]) + "\n"
        case "RawText":
            text += node["content"]
        case "Paragraph":
            mapping = {}
            paragraph = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            if len(re.findall(html_pattern, paragraph)):
                constant_id = get_constant_id(mapping)
                mapping[constant_id] = paragraph
                paragraph = constant_id
            if translator:
                paragraph = translate(translator, paragraph, translation_memo)
                sorted_mapping = sorted(mapping.items(), reverse=True)
                for constant_id, constant in sorted_mapping:
                    paragraph = paragraph.replace(constant_id, constant)
            text += paragraph + "\n\n"
        case "Link":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            converted_text = f'[{text_children}]({node["target"]})'
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "SetextHeading":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            heading_c = "=-"[node["level"] - 1]
            text += text_children + "\n"
            text += heading_c * len(text_children) + "\n"
        case "Emphasis":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            converted_text = "*" + text_children + "*"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "Strong":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            converted_text = "**" + text_children + "**"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "Strikethrough":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            converted_text = "~~" + text_children + "~~"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "List":
            # TODO: loose, start
            text_children = "".join([node_to_text(child, list_depth + 1) for child in node["children"]])
            text += text_children
        case "ListItem":
            text_children = "".join([node_to_text(child, list_depth) for child in node["children"]])
            text += ("  " * (list_depth - 1)) + node["leader"] + " " + text_children
        case "LineBreak":
            text += "\n"
        case "AutoLink":
            converted_text = "<" + "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]]) + ">"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "Image":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            converted_text = f'![{text_children}]({node["src"]} "{node["title"]}")'
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "InlineCode":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            converted_text = "`" + text_children + "`"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "CodeFence":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            text += "```" + node["language"] + "\n" + text_children + "```\n"
        case "Table":
            pass
        case "Quote":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo) for child in node["children"]])
            text += "> " + text_children
        case "ThematicBreak":
            text += "---\n"
        case _:
            assert False, json.dumps(node)
    return text


def translate_md(args, translator, translation_memo):
    file = Path(args.FILENAME).open("r")
    doc = Document(file)
    ast = ast_renderer.get_ast(doc)
    print(node_to_text(ast, translator=translator, translation_memo=translation_memo))
