import json
import re
from pathlib import Path

from mistletoe import Document, ast_renderer

from .utils_deepl import *

html_pattern = re.compile(r"(<(\".*?\"|'.*?'|[^'\"])*?>)+", re.MULTILINE | re.DOTALL)

def get_constant_id(mapping):
    return "X" + str(len(mapping)).zfill(2)

def postprocess(text: str, mapping: dict):
    sorted_mapping = sorted(mapping.items(), reverse=True)
    for constant_id, constant in sorted_mapping:
        text = text.replace(constant_id, constant)
    return text

def node_to_text(node, list_depth=0, translator=None, mapping=None, translation_memo=None, check=False) -> str:
    text = ""
    match node["type"]:
        case "Document":
            text += "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
        case "Heading":
            assert len(node["children"]) == 1
            text += ("#" * node["level"]) + " " + node_to_text(node["children"][0]) + "\n"
        case "RawText":
            text += node["content"]
        case "Paragraph":
            mapping = {}
            paragraph = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            if len(re.findall(html_pattern, paragraph)):
                constant_id = get_constant_id(mapping)
                mapping[constant_id] = paragraph
                paragraph = constant_id
            if translator:
                paragraph = translate(translator, paragraph, translation_memo, check)
                paragraph = postprocess(paragraph, mapping)
            text += paragraph + "\n\n"
        case "Link":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            converted_text = f'[{text_children}]({node["target"]})'
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "SetextHeading":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            heading_c = "=-"[node["level"] - 1]
            text += text_children + "\n"
            text += heading_c * len(text_children) + "\n"
        case "Emphasis":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            converted_text = "*" + text_children + "*"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "Strong":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            converted_text = "**" + text_children + "**"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "Strikethrough":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            converted_text = "~~" + text_children + "~~"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "List":
            # TODO: loose, start
            text_children = "".join([node_to_text(child, list_depth + 1, translator, mapping, translation_memo, check) for child in node["children"]])
            text += text_children
        case "ListItem":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            text += ("  " * (list_depth - 1)) + node["leader"] + " " + text_children
        case "LineBreak":
            text += "\n"
        case "AutoLink":
            converted_text = "<" + "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]]) + ">"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "Image":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            if node["title"]:
                converted_text = f'![{text_children}]({node["src"]} "{node["title"]}")'
            else:
                converted_text = f'![{text_children}]({node["src"]})'
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "InlineCode":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            converted_text = "`" + text_children + "`"
            if translator:
                constant_id = get_constant_id(mapping)
                text += constant_id
                mapping[constant_id] = converted_text
            else:
                text += converted_text
        case "CodeFence":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            text += "```" + node["language"] + "\n" + text_children + "```\n"
        case "Table":
            mapping = {}
            column_align = node["column_align"]
            table = node_to_text(node["header"], list_depth, translator, mapping, translation_memo, check)
            table += ""
            for align in column_align:
                table += "|"
                match align:
                    case None:
                        table += "-"
                    case 0:
                        table += ":-:"
                    case 1:
                        table += "-:"
                    case _:
                        assert False
            table += "|\n"
            table += "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            table += "\n"
            text += postprocess(table, mapping)
        case "TableRow":
            text_children = "|".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            text += "|" + text_children + "|\n"
        case "TableCell":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            text += text_children
        case "Quote":
            text_children = "".join([node_to_text(child, list_depth, translator, mapping, translation_memo, check) for child in node["children"]])
            text += "> " + text_children
        case "ThematicBreak":
            text += "---\n"
        case _:
            assert False, json.dumps(node)
    return text


def translate_md(args, translator, translation_memo):
    lines = Path(args.FILENAME).open("r").readlines()
    metadata = ""
    if lines[0] == "---\n":
        for i, line in enumerate(lines[1:]):
            if line == "---\n":
                metadata, lines = "".join(lines[:i+1]), lines[i+1:]
                break

    doc = Document(lines)
    ast = ast_renderer.get_ast(doc)
    if args.ast:
        return json.dumps(ast)
    else:
        return metadata + node_to_text(ast, translator=translator, translation_memo=translation_memo, check=args.check)
