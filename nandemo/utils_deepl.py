import sys


def translate(translator, text, translation_memo, check=False):
    if text == "":
        translated_text = ""
    elif check:
        translated_text = text
    elif text in translation_memo:
        translated_text = translation_memo[text]
    else:
        print("[DEBUG] translate:", text, file=sys.stderr)
        translated_text = str(translator.translate_text(text, target_lang="JA"))
        translation_memo[text] = translated_text
    return translated_text
