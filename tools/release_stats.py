# /// script
# dependencies = [
#   "pypistats",
#   "requests",
# ]
# ///

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pypistats
import requests

URL = 'https://api.github.com/repos/PalmSens/PalmSens_SDK/releases'
CACHE = Path('releases.json')


def get_pypi_downloads() -> int:
    ret = pypistats.overall('pypalmsens', format='json')
    data = json.loads(ret)['data']

    for row in data:
        if row['category'] == 'without_mirrors':
            return row['downloads']

    return 0


if not CACHE.exists():
    result = requests.get(URL)
    data = json.loads(result.text)
    print('read from url')
    with CACHE.open('w') as f:
        json.dump(data, f)
else:
    with CACHE.open() as f:
        data = json.load(f)
    print('read from cache')

count: dict[str, int] = defaultdict(int)

for release in data:
    tag = release['tag_name']

    if tag == 'python-1.0.0':
        tag = 'drivers-5.12'

    component = tag.split('-')[0]

    assets = release['assets']

    if assets:
        downloads = sum(asset['download_count'] for asset in assets)
        count[f'{component} (github)'] += downloads

        print

count['python (pypi)'] = get_pypi_downloads()

print('\n# Total downloads')
for k, v in count.items():
    print(f'{k:18} {v:>10}')
