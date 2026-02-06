# Building the docs

The docs are written in the [asciidoc](https://asciidoc.org/) ([docs](https://docs.asciidoctor.org/asciidoc/latest/syntax-quick-reference/)) format and built using [Antora](https://antora.org).

1. Install [Antora](https://docs.antora.org/antora/latest/install-and-run-quickstart/)

2. Build the docs:

```
npx antora antora-playbook.yml
```

Building the Python api docs is automated through the [collector extension](https://docs.antora.org/collector-extension/latest/).

To build the Python docs manually, run:

```bash
cd python
python python/build_python_api_docs.py
```

## UI

The UI is derived from the [antora default UI](https://gitlab.com/antora/antora-ui-default/-/tree/master/src)
