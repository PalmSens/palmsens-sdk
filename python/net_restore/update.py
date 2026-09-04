from __future__ import annotations

import argparse
import subprocess as sp
import sys
import time
from dataclasses import dataclass
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


linux_x64 = Spec(
    rid='linux-x64',
    name='linux-x64',
    project='mono.csproj',
)
linux_arm64 = Spec(
    rid='linux-arm64',
    name='linux-arm64',
    project='mono.csproj',
)
osx_arm64 = Spec(
    rid='osx-arm64',
    name='osx-arm64',
    project='mono.csproj',
)
osx_x64 = Spec(
    rid='osx-x64',
    name='osx-x64',
    project='mono.csproj',
)
win = Spec(
    rid='win-x64',
    name='win',
    project='windows.csproj',
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

        # sys.exit()


if __name__ == '__main__':
    main()
