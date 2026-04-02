from __future__ import annotations

import datetime
import json
import subprocess as sp
import sys
from textwrap import dedent


def get_releases(name: str = 'python') -> list[str]:
    cmd = 'gh release list'.split()
    p = sp.run(cmd, capture_output=True)
    lines = p.stdout.decode().splitlines()

    releases = []

    for line in lines:
        tag = line.split('\t')[2]
        if tag.startswith(name):
            releases.append(tag)

    return releases


releases = sys.argv[1:]

if not releases:
    releases = get_releases()

for release in releases:
    name, version = release.split('-')

    try:
        with open(f'{release}.json') as f:
            data = json.load(f)
    except IOError:
        cmd = f'gh release view {release} --json name,body,url,tagName,publishedAt'.split()
        p = sp.run(cmd, capture_output=True)
        payload = p.stdout.decode()

        with open(f'{release}.json', 'w') as f:
            f.write(payload)

        data = json.loads(payload)

    time = datetime.datetime.fromisoformat(data['publishedAt'])

    TEMPLATE = dedent("""\
    # {name}

    > :fontawesome-brands-github: <a href="{url}">{tagName}</a>
    - :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/{version}">pypalmsens-{version}</a>
    - :fontawesome-solid-calendar: {time}

    {body}
    """)

    with open(f'{release}.md', 'w') as f:
        string = TEMPLATE.format(version=version, time=time.date(), **data)
        f.write(string)

    print(release)
