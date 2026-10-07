"""This is a simple script that generates examples for methods."""

from __future__ import annotations

import inspect
from textwrap import indent

import pypalmsens as ps
from pypalmsens._methods.base import BaseSettings


def get_settings_example(cls):
    settings = cls()
    fields = cls.model_fields  # type: ignore

    s = []

    s.append('Examples')
    s.append('--------')
    s.append('>>> import pypalmsens as ps')
    s.append(f'>>> from pypalmsens.settings import {cls.__name__}')
    s.append('>>> method = ps.CyclicVoltammetry(')
    s.append(f'...     {cls.__name__}(')

    for field in fields:
        if field == 'id':
            continue

        attr = getattr(settings, field)
        if not isinstance(attr, BaseSettings):
            s.append(f'...         {field}={attr!r},')

    s.append('...     ),')
    s.append('... )')

    return '\n'.join(s)


if __name__ == '__main__':
    prefix = ' ' * 4

    f = open('out.txt', 'w')

    for name in dir(ps.settings):
        if name in ('id',):
            continue

        cls = getattr(ps.settings, name)
        if not inspect.isclass(cls):
            continue

        if not issubclass(cls, BaseSettings):
            continue

        s = get_settings_example(cls)
        s = indent(s, prefix=prefix)

        _ = f.write(s)
        _ = f.write('\n\n')

    f.close()
