import sys
import colorama

def translate(translator, text, translation_memo, check=False):
    if text == "":
        translated_text = ""
    elif check:
        print("[DEBUG] check translate:", text, file=sys.stderr)
        translated_text = text
    elif text in translation_memo:
        translated_text = translation_memo[text]
    else:
        print("[DEBUG] translate:", text, file=sys.stderr)
        translated_text = str(translator.translate_text(text, target_lang="JA"))
        translation_memo[text] = translated_text
    for line in text.splitlines():
        if not (line[0].isupper() and line[-1] in ".:"):
            print(f"{colorama.Fore.YELLOW}[WARNING] The following text is not capitalized or does not end with a period/colon: \n  {line}{colorama.Style.RESET_ALL}", file=sys.stderr)
    return translated_text
