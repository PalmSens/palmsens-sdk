from __future__ import annotations

import argparse
import os
import shutil
import subprocess as sp
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

for exe in ('gh', 'bump-my-version'):
    assert shutil.which(exe)

ROOT = Path(__file__).parents[1]

PR_BODY = """\
This PR prepares for a new release of the {sdk} SDK.

- branch: `release-{sdk.tag}`
- version: `{sdk.version}`
- sdk: `{sdk.name}`
"""


@dataclass
class SDK:
    name: Literal['python', 'matlab', 'maui', 'wpf', 'labview', 'winforms']
    version: str = ''

    def old_version(self):
        """Get current version."""
        cmd = ['bump-my-version', 'show', 'current_version']

        with self.chdir():
            p = sp.run(cmd, capture_output=True)

        return p.stdout.decode().strip()

    def bump(self, component: Literal['major', 'minor', 'patch']) -> SDK:
        cmd = ['bump-my-version', 'show', '--increment', component, 'new_version']

        with self.chdir():
            p = sp.run(cmd, capture_output=True)

        new_version = p.stdout.decode().strip()
        return SDK(self.name, new_version)

    @property
    def tag(self) -> str:
        return f'{self.name}-{self.version}'

    @property
    def workdir(self) -> Path:
        return ROOT / self.name

    @contextmanager
    def chdir(self):
        prev_cwd = Path.cwd().resolve()
        try:
            os.chdir(self.workdir)
            yield
        finally:
            os.chdir(prev_cwd)


def commit_file(path: str | Path, message: str):
    sp.check_call(['git', 'add', f'{path}'])
    sp.check_call(['git', 'commit', '-m', message])


def update_releases(sdk: SDK, commit: bool = False):
    releases_path = Path(ROOT, 'docs', 'sdk', 'modules', 'ROOT', 'pages', 'releases.adoc')
    assert releases_path.exists()
    lines = releases_path.read_text().splitlines()

    index = lines.index('// latest')

    if sdk.tag in lines[index + 1]:
        print('Tag already exists, skipping')
    else:
        new_line = (
            f'- https://github.com/palmsens/palmsens_sdk/releases/tag/{sdk.tag}[{sdk.tag}]'
        )
        lines.insert(index + 1, new_line)
        releases_path.write_text('\n'.join(lines) + '\n', encoding='UTF-8')
        print(f'Tag added to {releases_path.name}')

    if commit:
        commit_file(releases_path, message='Updated release index')


def bump_version_to(sdk: SDK):
    with sdk.chdir():
        sp.check_call(
            [
                'bump-my-version',
                'bump',
                '--new-version',
                sdk.version,
                'patch',
                '--commit',
            ]
        )

    print(f'Set {sdk.name} version to {sdk.version}')


def prepare_release_branch(sdk: SDK, base_branch: str) -> str:
    sp.check_call(['git', 'checkout', f'origin/{base_branch}'])

    release_branch = f'release-{sdk.tag}'

    sp.run(
        ['git', 'checkout', '-b', release_branch, f'origin/{base_branch}'],
        check=True,
    )

    print(f'Created branch {release_branch}')

    return release_branch


def push_branch_and_create_pr(sdk: SDK, base_branch: str, release_branch: str):
    sp.run(
        ['git', 'push', 'origin', f'HEAD:{release_branch}', '--force'],
        check=True,
    )
    print(f'Pushed {release_branch}')

    body = PR_BODY.format(version=sdk.version, sdk=sdk, tag=sdk.tag)
    print(body)

    sp.run(
        [
            'gh',
            'pr',
            'create',
            f'--base={base_branch}',
            f'--head={release_branch}',
            f'--title=Release {sdk.tag}',
            f'--body={body}',
            '--draft',
        ],
        check=True,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sdk', type=str)
    parser.add_argument('--version', type=str, help='Set version.')
    parser.add_argument('--bump', type=str, help='Major/minor/patch, overrides version.')
    options = parser.parse_args()

    if options.bump:
        sdk = SDK(options.sdk)
        sdk = sdk.bump(component=options.bump)
    else:
        sdk = SDK(options.sdk, options.version)

    print(f'New version: {sdk.tag=}')

    base_branch = 'main'

    release_branch = prepare_release_branch(sdk=sdk, base_branch=base_branch)
    update_releases(sdk=sdk, commit=True)

    if sdk.name == 'python':
        import changelog

        changelog.update_python(new_tag=sdk.tag)

    bump_version_to(sdk)

    push_branch_and_create_pr(sdk=sdk, release_branch=release_branch, base_branch=base_branch)
