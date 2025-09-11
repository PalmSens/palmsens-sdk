# Development

## Setup

Clone the repository into the `palmsens-sdk` directory:

```console
git clone https://github.com/palmsens/palmsens-sdk
```

Install using `virtualenv`:

```console
cd palmsens-sdk/python
python3 -m venv .venv
source .venv/Scripts/activate.ps1
python3 -m pip install -e .[develop]
```

## Running tests

The PalmSens Python SDK uses [pytest](https://docs.pytest.org/en/latest/) to run the tests. You can run the tests for yourself using:

```console
pytest
```

To skip the tests that require a connected instrument use the `requires_instrument` [marker](https://docs.pytest.org/en/latest/example/markers.html):

```console
pytest -m "not examples"
```

To check coverage:

```console
coverage run -m pytest
coverage report  # to output to terminal
coverage html    # to generate html report
```

## Running linters and code formatters

The PalmSens Python SDK uses [ruff](https://astral.sh/ruff) for code [formatting](https://docs.astral.sh/ruff/formatter/)/[linting](https://docs.astral.sh/ruff/linter/), and [mypy](https://www.mypy-lang.org/) for type checking.
[pre-commit](https://pre-commit.com/) is a tool that can run many tools for checking code quality with a single command.
Based on the filetype it can select which tool to run.

By default, pre-commit will only run on the staged files:

```
pre-commit run
```

To check a specific file, use:

```
pre-commit run --files your_script.py
```

Configure `pre-commit` to run on every commit by installing it as a [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks):

```
pre-commit install
```

The commit will be aborted if it finds any issues.
Some issues can be fixed automatically (e.g. code formatting, import sorting).
To bypass the check, run:

```
git commit --no-verify
```

## Documentation

The documentation uses [griffe2md](https://mkdocstrings.github.io/griffe2md/) and pandoc to build the API documentation.

The code uses the [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) style for docstrings, and [PEP-257 style](https://peps.python.org/pep-0257/#what-is-a-docstring) attribute docstrings.

The build script defines which classes and modules to document.

```bash
python build_python_api_docs.py
```

## Making a release

PyPalmSens uses [SemVer](http://semver.org/) versioning scheme.

1. Bump the version (`major`/`minor`/`patch` as needed), see [bump-my-version](https://github.com/callowayproject/bump-my-version).

```console
bump-my-version minor
```

2. Make a release on [GitHub](https://github.com/PalmSens/PalmSens_SDK/releases).

The **release tag must start with `'python-'`**. This triggers the automated publish to [PyPi](https://pypi.org/project/pypalmsens).

To manually publish:

```bash
pip install twine build
python -m build
twine upload dist/*
```
