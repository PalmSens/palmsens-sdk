from __future__ import annotations

import argparse
import subprocess as sp
import sys
import time
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Literal

LIBPALMSENS_DIR = Path('../src/pypalmsens/_libpalmsens')


@dataclass
class PlatformBuild:
    rid: Literal[
        'win-x64',
        'win-x86',
        'win-arm64',
        'osx-x64',
        'osx-arm64',
        'linux-x64',
        'linux-arm64',
        'linux-arm',
    ]
    """NET runtime identifier."""
    name: str
    """Directory name."""
    project: str
    """Project to run."""
    to_remove: list[str] = field(default_factory=list)
    """Files to remove afterwards."""
    to_rename: list[tuple[str, str]] = field(default_factory=list)

    def remove_shim_files(self, target_dir: Path):
        for name in self.to_remove:
            to_remove = target_dir / name
            assert to_remove.exists()
            to_remove.unlink()

    def rename_files(self, target_dir: Path):
        for _from, _to in self.to_rename:
            src = target_dir / _from
            dst = target_dir / _to
            assert src.exists()
            dst.unlink(missing_ok=True)
            _ = src.rename(dst)


mono_delete = ['mono.dll', 'mono', 'mono.pdb', 'mono.deps.json']
mono_rename = [('mono.runtimeconfig.json', 'runtimeconfig.json')]


linux_x64 = PlatformBuild(
    rid='linux-x64',
    name='linux-x64',
    project='mono.csproj',
    to_remove=mono_delete,
    to_rename=mono_rename,
)
linux_arm64 = PlatformBuild(
    rid='linux-arm64',
    name='linux-arm64',
    project='mono.csproj',
    to_remove=mono_delete,
    to_rename=mono_rename,
)
osx_arm64 = PlatformBuild(
    rid='osx-arm64',
    name='osx-arm64',
    project='mono.csproj',
    to_remove=mono_delete,
    to_rename=mono_rename,
)
osx_x64 = PlatformBuild(
    rid='osx-x64',
    name='osx-x64',
    project='mono.csproj',
    to_remove=mono_delete,
    to_rename=mono_rename,
)
win = PlatformBuild(
    rid='win-x64',
    name='win',
    project='windows.csproj',
    to_remove=[
        'Microsoft.Windows.SDK.NET.dll',
        'windows.dll',
        'windows.exe',
        'windows.pdb',
        'windows.deps.json',
    ],
    to_rename=[('windows.runtimeconfig.json', 'runtimeconfig.json')],
)

PLATFORM_BUILDS = linux_x64, linux_arm64, osx_arm64, osx_x64, win


def main():
    out_dir = LIBPALMSENS_DIR.absolute()

    for build in PLATFORM_BUILDS:
        target_dir = (out_dir / build.name).resolve()

        print(f'>>> {build.project}:{build.rid}')

        cmd = (
            f'dotnet publish {build.project} '
            '--configuration Release '
            '--self-contained false '
            f'--output {target_dir} '
            f'--runtime {build.rid}'
        )

        _ = sp.run(cmd.split(), check=True)

        build.remove_shim_files(target_dir)
        build.rename_files(target_dir)


if __name__ == '__main__':
    main()
