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
class Spec:
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
    delete: list[str] = field(default_factory=list)
    """Files to remove afterwards."""
    rename: list[tuple[str, str]] = field(default_factory=list)


mono_delete=['mono.dll', 'mono', 'mono.pdb', 'mono.deps.json']
mono_rename=[('mono.runtimeconfig.json', 'runtimeconfig.json')]


linux_x64 = Spec(
    rid='linux-x64',
    name='linux-x64',
    project='mono.csproj',
    delete=mono_delete,
    rename=mono_rename,
)
linux_arm64 = Spec(
    rid='linux-arm64',
    name='linux-arm64',
    project='mono.csproj',
    delete=mono_delete,
    rename=mono_rename,
)
osx_arm64 = Spec(
    rid='osx-arm64',
    name='osx-arm64',
    project='mono.csproj',
    delete=mono_delete,
    rename=mono_rename,
)
osx_x64 = Spec(
    rid='osx-x64',
    name='osx-x64',
    project='mono.csproj',
    delete=mono_delete,
    rename=mono_rename,
)
win = Spec(
    rid='win-x64',
    name='win',
    project='windows.csproj',
    delete=['windows.dll', 'windows.exe', 'windows.pdb', 'windows.deps.json'],
    rename=[('windows.runtimeconfig.json', 'runtimeconfig.json')]
)

specs = linux_x64, linux_arm64, osx_arm64, osx_x64, win


def main():
    parser = argparse.ArgumentParser(prog='myprogram')
    parser.add_argument('--source', type=Path, help='Local package source')
    parser.add_argument('--out', type=Path, help='Output directory', default=LIBPALMSENS_DIR)

    args = parser.parse_args()

    # source_dir = args.source.absolute()
    out_dir = args.out.absolute()

    for spec in specs:
        target_dir = (out_dir / spec.name).resolve()
        # target_dir = Path(spec.directory + str(int(time.time()))).resolv()

        print()
        print(spec)

        cmd = (
            f'dotnet publish {spec.project} '
            '--configuration Release '
            '--self-contained false '
            f'--output {target_dir} '
            f'--runtime {spec.rid}'
        )

        # print(cmd)
        _ = sp.run(cmd.split(), check=True)

        for name in spec.delete:
            to_remove = target_dir / name
            assert to_remove.exists()
            to_remove.unlink()

        for _from, _to in spec.rename:
            src = target_dir / _from
            dst = target_dir / _to
            assert src.exists()
            dst.unlink(missing_ok=True)
            src.rename(dst)

        # sys.exit()


if __name__ == '__main__':
    main()
