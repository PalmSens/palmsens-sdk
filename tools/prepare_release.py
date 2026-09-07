from __future__ import annotations

import argparse
import json
import shutil
import subprocess as sp
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).parents[1]


for exe in ('gh', 'bump-my-version'):
    if not shutil.which(exe):
        sys.exit(f'{exe} is not installed or not on PATH')

PR_BODY = """\
This PR prepares for a new release of the {sdk.name} SDK.

- branch: `release-{sdk.tag}`
- version: `{sdk.version}`
- sdk: `{sdk.name}`

# Release notes

{body}
"""


@dataclass
class SDK:
    name: Literal['python', 'matlab', 'maui', 'wpf', 'labview', 'winforms']
    version: str = ''

    def old_version(self):
        """Get current version."""
        cmd = ['bump-my-version', 'show', 'current_version']

        p = sp.run(cmd, capture_output=True, check=True, cwd=self.workdir)

        return p.stdout.decode().strip()

    def bump(self, component: Literal['major', 'minor', 'patch']) -> SDK:
        cmd = ['bump-my-version', 'show', '--increment', component, 'new_version']

        p = sp.run(cmd, capture_output=True, check=True, cwd=self.workdir)

        new_version = p.stdout.decode().strip()
        return SDK(self.name, new_version)

    @property
    def tag(self) -> str:
        return f'{self.name}-{self.version}'

    @property
    def workdir(self) -> Path:
        return ROOT / self.name


def commit_file(path: str | Path, message: str):
    _ = sp.check_call(['git', 'add', f'{path}'])
    _ = sp.check_call(['git', 'commit', '-m', message])


def update_releases(sdk: SDK, commit: bool = False):
    releases_path = Path(ROOT, 'docs', 'sdk', 'modules', 'ROOT', 'pages', 'releases.adoc')

    if not releases_path.exists():
        sys.exit(f'{releases_path} does not exist')

    lines = releases_path.read_text().splitlines()

    index = lines.index('// latest')

    if any(sdk.tag in line for line in lines):
        print('Tag already exists, skipping')
    else:
        new_line = (
            f'- https://github.com/palmsens/palmsens-sdk/releases/tag/{sdk.tag}[{sdk.tag}]'
        )
        lines.insert(index + 1, new_line)
        releases_path.write_text('\n'.join(lines) + '\n', encoding='UTF-8')
        print(f'Tag added to {releases_path.name}')

    if commit:
        commit_file(releases_path, message='Updated release index')


def bump_version_to(sdk: SDK):
    sp.check_call(
        [
            'bump-my-version',
            'bump',
            '--new-version',
            sdk.version,
            'patch',
            '--commit',
            '--allow-dirty',
        ],
        cwd=sdk.workdir,
    )

    print(f'Set {sdk.name} version to {sdk.version}')


def assert_clean_worktree():
    p = sp.run(['git', 'status', '--porcelain'], capture_output=True, check=True)
    status = p.stdout.decode().strip()
    if status:
        raise RuntimeError(f'Git working tree is not clean:\n\n{status}')


def prepare_release_branch(base_branch: str, release_branch: str):
    assert_clean_worktree()

    sp.check_call(['git', 'fetch', 'origin'])

    sp.check_call(['git', 'checkout', f'origin/{base_branch}'])

    sp.check_call(['git', 'checkout', '-b', release_branch, f'origin/{base_branch}'])

    print(f'Created branch {release_branch}')


def push_branch_and_create_pr(sdk: SDK, *, body: str, base_branch: str, release_branch: str):
    sp.run(
        ['git', 'push', 'origin', f'HEAD:{release_branch}', '--force'],
        check=True,
    )
    print(f'Pushed {release_branch}')

    body = PR_BODY.format(body=body, sdk=sdk)
    print(body)

    p = sp.run(
        [
            'gh',
            'pr',
            'create',
            f'--base={base_branch}',
            f'--head={release_branch}',
            f'--title=Release {sdk.tag}',
            f'--body={body}',
            '--draft',
            '--json',
            'url',
        ],
        capture_output=True,
        check=True,
    )
    pr_url = json.loads(p.stdout)['url']
    print(f'PR created: {pr_url}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'sdk',
        type=str,
        choices=['python', 'matlab', 'maui', 'wpf', 'labview', 'winforms'],
    )
    parser.add_argument('--version', type=str, help='Set version.')
    parser.add_argument('--bump', type=str, help='Major/minor/patch, overrides version.')
    options = parser.parse_args()

    if options.bump:
        sdk = SDK(options.sdk)
        sdk = sdk.bump(component=options.bump)
    else:
        sdk = SDK(options.sdk, options.version)

    if not sdk.version:
        sys.exit('Specify --version or --bump.')

    current_version = sdk.old_version()
    if current_version == sdk.version:
        sys.exit(f'{sdk.name} is already at version {sdk.version}; nothing to do.')

    print(f'Current version: {current_version}')
    print(f'New version: {sdk.tag=}')

    base_branch = 'main'
    release_branch = f'release-{sdk.tag}'

    prepare_release_branch(base_branch=base_branch, release_branch=release_branch)
    update_releases(sdk=sdk, commit=True)

    if sdk.name == 'python':
        import changelog

        gh_body = changelog.update_python(new_tag=sdk.tag, new_version=sdk.version)
    else:
        gh_body = '-'

    bump_version_to(sdk)

    push_branch_and_create_pr(
        sdk=sdk, body=gh_body, release_branch=release_branch, base_branch=base_branch
    )

    if sdk.name == 'python':
        title = 'PyPalmSens'
        notesopt = f'--notes-file {ROOT / "changelog-python.md"}'
    else:
        title = sdk.name
        notesopt = '--generate-notes'

    print(f"""
Push additional changes to branch:

    git push origin release-{sdk.name}-{sdk.version}

Merge PR:

    gh pr merge $PR --squash

Make new release:

    gh release create {sdk.tag} --draft --title "{title} {sdk.version}" {notesopt}
""")
