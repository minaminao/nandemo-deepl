# Nandemo DeepL
Nandemo DeepL is a tool to translate various file formats with DeepL.

## Supported File Formats
- Markdown (.md)
- reStructuredText (.rst)

## Install
```sh
pip install -e .
```

## Usage
```sh
export DEEPL_API_KEY=<YOUR API KEY>
nandemo samples/sample.md
```

```sh
nandemo foo.md
```

Back up the original file:
```
nandemo --backup foo.md
```

## 注意
- Markdownで、パラグラフ内で英文が途中で改行されている場合、改行されたまま翻訳される。