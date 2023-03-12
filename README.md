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
nandemo foo/*.md
```

Back up the original files:
```
nandemo --backup foo/*.md
```

