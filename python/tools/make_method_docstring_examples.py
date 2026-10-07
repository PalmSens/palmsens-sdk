"""This is a simple script that generates examples for methods."""

from __future__ import annotations

from textwrap import indent

import pypalmsens as ps
from pypalmsens._methods.base import BaseSettings, BaseTechnique

ids = (
    'acv',
    'ad',
    'cc',
    'cp',
    'cpot',
    'cv',
    'dpv',
    'eis',
    # 'eis_it',
    'fam',
    'fcv',
    'fgis',
    'fis',
    # 'geis_it',
    'gis',
    'gs',
    'lp',
    'lsp',
    'lsv',
    'ma',
    'mm',
    'mp',
    'mpad',
    'ms',
    'npv',
    'ocp',
    'pad',
    'pot',
    'ps',
    'scp',
    'swv',
)


def get_class_example(id: str):
    cls = BaseTechnique._registry[id]

    method = cls()
    fields = cls.model_fields  # type: ignore

    s = []

    s.append('Examples')
    s.append('--------')
    s.append('>>> import pypalmsens as ps')
    s.append(f'>>> method = ps.{cls.__name__}(')

    for field in fields:
        if field == 'id':
            continue
        if field in (
            'enable_bipot_current',
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'record_we_current',
        ):
            continue
        attr = getattr(method, field)
        if not isinstance(attr, BaseSettings):
            s.append(f'...     {field}={attr!r},')

    s.append('... )')

    return '\n'.join(s)


method = ps.MethodScript(
    version='1.10',
    script="""wait 100m
    if 1 < 2
        send_string "Hello world"
    endif""",
)

if __name__ == '__main__':
    prefix = ' ' * 4

    with open('out.txt', 'w') as f:
        for id in ids:
            s = get_class_example(id)
            s = indent(s, prefix=prefix)

            _ = f.write(s)
            _ = f.write('\n\n')
