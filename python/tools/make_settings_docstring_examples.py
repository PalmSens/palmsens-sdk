"""This is a simple script that generates examples for methods."""

from __future__ import annotations

from textwrap import indent

import pypalmsens as ps
from pypalmsens._methods.base import BaseSettings

SETTINGS = {
    'current_range': ps.settings.CurrentRange,
    'potential_range': ps.settings.PotentialRange,
    'pretreatment': ps.settings.Pretreatment,
    'versus_ocp': ps.settings.VersusOCP,
    'bipot': ps.settings.BiPot,
    'post_measurement': ps.settings.PostMeasurement,
    'current_limits': ps.settings.CurrentLimits,
    'potential_limits': ps.settings.PotentialLimits,
    'charge_limits': ps.settings.ChargeLimits,
    'ir_drop_compensation': ps.settings.IrDropCompensation,
    'equilibrion_triggers': ps.settings.EquilibrationTriggers,
    'measurement_triggers': ps.settings.MeasurementTriggers,
    'delay_triggers': ps.settings.DelayTriggers,
    'multiplexer': ps.settings.Multiplexer,
    'data_processing': ps.settings.DataProcessing,
    'general': ps.settings.General,
    'material': ps.settings.Material,
}

example_technique = {
    'PotentialRange': 'ps.ChronoPotentiometry',
    'PotentialLimits': 'ps.ChronoPotentiometry',
    'ChargeLimits': 'ps.ChronoAmperometry',
    'DelayTriggers': 'ps.LinearSweepPotentiometry',
    'Multiplexer': 'ps.LinearSweepPotentiometry',
    'Material': 'ps.corrosion.CyclicPolarization',
}


def get_settings_example(name: str):
    cls = SETTINGS[name]
    cls_name = cls.__name__

    settings = cls()
    fields = cls.model_fields  # type: ignore

    technique = example_technique.get(cls_name, 'ps.CyclicVoltammetry')

    method = eval(technique)
    assert name in method.model_fields, (technique, cls_name, name)  # type: ignore

    s = []

    s.append('Examples')
    s.append('--------')
    s.append(f'As a `{cls_name}` instance:')
    s.append('')
    s.append('>>> import pypalmsens as ps')
    s.append(f'>>> from pypalmsens.settings import {cls_name}')
    s.append(f'>>> method = {technique}(')
    s.append(f'...     {name}={cls_name}(')

    for field in fields:
        if field == 'id':
            continue

        attr = getattr(settings, field)
        if not isinstance(attr, BaseSettings):
            s.append(f'...         {field}={attr!r},')

    s.append('...     ),')
    s.append('... )')
    s.append('')

    # as dict

    s.append(f'From a dict (coerced to a `{cls_name}` by Pydantic):')
    s.append('')

    s.append(f'>>> method = {technique}(')
    s.append(f'...     {name}={{')

    for field in fields:
        if field == 'id':
            continue

        attr = getattr(settings, field)
        if not isinstance(attr, BaseSettings):
            s.append(f'...         {field!r}: {attr!r},')

    s.append('...     },')
    s.append('... )')
    s.append('')

    # as attributes

    s.append('By setting attributes directly:')
    s.append('')

    s.append(f'>>> method = {technique}()')

    for field in fields:
        if field == 'id':
            continue

        attr = getattr(settings, field)
        if not isinstance(attr, BaseSettings):
            s.append(f'>>> method.{name}.{field} = {attr!r}')

    return '\n'.join(s)


if __name__ == '__main__':
    prefix = ' ' * 4

    with open('out.txt', 'w') as f:
        for name in SETTINGS:
            s = get_settings_example(name)
            s = indent(s, prefix=prefix)

            _ = f.write(s)
            _ = f.write('\n\n')
