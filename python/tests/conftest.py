from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

TESTS = Path(__file__).parent


@dataclass(frozen=True)
class Suite:
    name: str
    short: str
    subdir: str
    default: bool
    description: str


SUITES: list[Suite] = [
    Suite(
        name='offline',
        short='O',
        subdir='offline',
        default=True,
        description='offline logic: data structures, IO, methods, dataclasses',
    ),
    Suite(
        name='instrument',
        short='I',
        subdir='instrument',
        default=False,
        description='requires an instrument connected over USB',
    ),
    Suite(
        name='lablink',
        short='L',
        subdir='lablink',
        default=False,
        description='requires a running lablink server with an attached instrument',
    ),
]


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup('suites', 'test suite selection')
    for suite in SUITES:
        group.addoption(
            f'-{suite.short}',
            f'--{suite.name}',
            action='store_true',
            help=f'{suite.description}{" [default]" if suite.default else ""}',
        )


def pytest_configure(config: pytest.Config) -> None:
    for suite in SUITES:
        config.addinivalue_line('markers', f'{suite.name}: {suite.description}')


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # collect suites
    flagged = {suite.name for suite in SUITES if config.getoption(suite.name)}
    if flagged:  # explicit flags win
        wanted: set[str] | None = flagged
    elif any(not arg.startswith('-') for arg in config.invocation_params.args):
        wanted = None  # explicit path: run what was collected
    else:
        wanted = {suite.name for suite in SUITES if suite.default}

    # tag each item with its suite, and partition
    kept: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        path = Path(item.path).resolve()
        for suite in SUITES:
            if path.is_relative_to(TESTS / suite.subdir):
                # `name` is now the item's suite
                break
        else:
            raise pytest.UsageError(
                f'{item.nodeid} is not inside a known suite directory '
                f'({", ".join(suite.subdir for suite in SUITES)}). '
                'Move the file into a suite directory, or add one to SUITES.'
            )

        # so `-m lablink` works
        item.add_marker(getattr(pytest.mark, suite.name))
        if wanted is not None and suite.name not in wanted:
            deselected.append(item)
        else:
            kept.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept
