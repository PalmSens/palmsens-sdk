# https://github.com/casey/just

set windows-shell := ['powershell.exe', '-NoProfile', '-NoLogo', '-Command']

list_version *ARGS:
    uv run tools/version.py {{ARGS}}

make_docs:
    npx antora antora-playbook.yml
