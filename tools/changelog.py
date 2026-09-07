from __future__ import annotations

import datetime
import subprocess as sp
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).parents[1]


def get_latest_tag(component: str = 'python'):
    cmd = ['git', 'tag', '--list', '--sort', '-creatordate']
    p = sp.run(cmd, capture_output=True, check=True)
    tags = p.stdout.decode().splitlines()
    for line in tags:
        if line.startswith(f'{component}-'):
            latest = line
            break
    else:
        raise ValueError(f'No tag matching {component!r} in tags: {tags}.')
    return latest


def get_changes_since_tag(tag: str):
    cmd = ['git', 'log', f'{tag}..HEAD', '--reverse', '--oneline']
    p = sp.run(cmd, capture_output=True, check=True)
    lines = p.stdout.decode().splitlines()
    lines = (line.split(maxsplit=1)[1] for line in lines)

    out = []
    skipped = []

    for line in lines:
        if '(#' not in line and not line.endswith(')'):
            skipped.append(line)
            continue

        if line.startswith('('):
            index = line.index(')')
            line = line[index + 2 :]

        index = line.index('(#')
        pr = line[index + 2 : -1]
        line = line.replace(
            f'#{pr}', f'[#{pr}](https://github.com/palmsens/palmsens-sdk/pull/{pr})'
        )
        out.append(f'- {line}')

    if skipped:
        print('Warning: commits not included in changelog:')
        for line in skipped:
            print(f'  - {line}')

    return '\n'.join(out)


def update_python(new_tag: str, new_version: str, previous_tag: str | None = None) -> str:
    if previous_tag is None:
        previous_tag = get_latest_tag()

    changelog = get_changes_since_tag(previous_tag)

    time = datetime.datetime.now(tz=datetime.UTC)

    TEMPLATE_CHANGELOG = dedent("""\
    ## PyPalmSens {new_version}

    > :fontawesome-brands-github: <a href="https://github.com/palmsens/palmsens-sdk/releases/tag/{new_tag}">{new_tag}</a>
    | :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/{new_version}">pypalmsens-{new_version}</a>
    | :fontawesome-solid-calendar: {time}

    ### What's changed

    {changelog}

    """)

    TEMPLATE_GH_RELEASES = dedent("""\
    PyPalmSens {new_version} is now available on PyPi.

    To upgrade: `pip install pypalmsens -U`.

    For more information, see [the documentation](https://dev.palmsens.com/python/latest/_attachments/releases/#{anchor})

    ## What's changed

    {changelog}

    **Full Changelog**: https://github.com/palmsens/palmsens-sdk/compare/{previous_tag}...{new_tag}
    """)

    index_path = Path(ROOT / 'python' / 'docs' / 'zensical' / 'releases' / 'index.md')

    lines = index_path.read_text().splitlines()

    index = lines.index('<!-- Latest-->')

    if new_version in lines[index + 1]:
        print('Tag already exists, skipping')
    else:
        new_string = TEMPLATE_CHANGELOG.format(
            new_version=new_version,
            new_tag=new_tag,
            time=time.date(),
            changelog=changelog,
        )
        print(new_string)

        lines.insert(index + 1, new_string)
        index_path.write_text('\n'.join(lines) + '\n', encoding='UTF-8')

        print(f'Tag added to {index_path.name}')

    gh_releases = TEMPLATE_GH_RELEASES.format(
        new_version=new_version,
        new_tag=new_tag,
        previous_tag=previous_tag,
        time=time.date(),
        changelog=changelog,
        anchor='pypalmsens-' + new_version.replace('.', ''),
    )

    notes_path = ROOT / 'changelog-python.md'

    with open(notes_path, 'w') as f:
        f.write(gh_releases)

    return gh_releases


if __name__ == '__main__':
    component = 'python'
    args = sys.argv[1:]

    if len(args) != 2:
        sys.exit(f'usage: {sys.argv[0]} <previous_version> <new_version>')

    previous_version, new_version = args
    previous_tag = f'{component}-{previous_version}'
    new_tag = f'{component}-{new_version}'

    update_python(new_tag, new_version, previous_tag)
