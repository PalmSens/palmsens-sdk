from __future__ import annotations

import pytest
from PalmSens import AutoRanging, AutoRangingPotential

import pypalmsens as ps
from pypalmsens._methods import (
    cr_string_to_enum,
    pr_string_to_enum,
)


def test_current_range():
    assert str(cr_string_to_enum('100pA')) == '100 pA'
    assert str(cr_string_to_enum('1A')) == '1 A'
    assert str(cr_string_to_enum('63uA')) == '63 uA'

    with pytest.raises(AttributeError):
        _ = cr_string_to_enum('foo')
        _ = cr_string_to_enum(123)


def test_potential_range():
    assert str(pr_string_to_enum('1mV')) == '1 mV'
    assert str(pr_string_to_enum('100mV')) == '100 mV'
    assert str(pr_string_to_enum('1V')) == '1 V'

    with pytest.raises(AttributeError):
        pr_string_to_enum('foo')
        pr_string_to_enum(123)


def test_method_current_range():
    crmin = '100nA'
    crmax = '1mA'
    crstart = '100uA'

    method = ps.CyclicVoltammetry(
        current_range=ps.settings.CurrentRange(
            min=crmin,
            max=crmax,
            start=crstart,
        )
    )
    obj = method._to_psmethod()

    supported_ranges = obj.Ranging.SupportedCurrentRanges

    assert cr_string_to_enum(crmin) in supported_ranges
    assert cr_string_to_enum(crmax) in supported_ranges
    assert cr_string_to_enum(crstart) in supported_ranges

    assert obj.Ranging.MinimumCurrentRange.Description == '100 nA'
    assert obj.Ranging.MaximumCurrentRange.Description == '1 mA'
    assert obj.Ranging.StartCurrentRange.Description == '100 uA'


def test_method_potential_range():
    potmin = '1mV'
    potmax = '100mV'
    potstart = '10mV'

    method = ps.ChronoPotentiometry(
        potential_range=ps.settings.PotentialRange(
            min=potmin,
            max=potmax,
            start=potstart,
        )
    )
    obj = method._to_psmethod()
    supported_ranges = obj.RangingPotential.SupportedPotentialRanges

    assert pr_string_to_enum(potmin) in supported_ranges
    assert pr_string_to_enum(potmax) in supported_ranges
    assert pr_string_to_enum(potstart) in supported_ranges

    assert obj.RangingPotential.MinimumPotentialRange.Description == '1 mV'
    assert obj.RangingPotential.MaximumPotentialRange.Description == '100 mV'
    assert obj.RangingPotential.StartPotentialRange.Description == '10 mV'


def test_method_current_range_clipping():
    ranging = AutoRanging(
        minRange=cr_string_to_enum('100nA'),
        maxRange=cr_string_to_enum('1mA'),
        startRange=cr_string_to_enum('100uA'),
    )

    cr_outside = cr_string_to_enum('5mA')
    assert cr_outside not in ranging.SupportedCurrentRanges

    # Check that start range gets clipped to max range
    ranging.StartCurrentRange = cr_outside
    assert ranging.StartCurrentRange.Description == '1 mA'

    # Check that max range gets clipped to nearest supported range
    ranging.MaximumCurrentRange = cr_outside
    assert ranging.MaximumCurrentRange.Description == '10 mA'


def test_method_potential_range_clipping():
    ranging = AutoRangingPotential(
        minRange=pr_string_to_enum('1mV'),
        maxRange=pr_string_to_enum('100mV'),
        startRange=pr_string_to_enum('10mV'),
    )

    pot_outside = pr_string_to_enum('500mV')
    assert pot_outside not in ranging.SupportedPotentialRanges

    # Check that start range gets clipped to max range
    ranging.StartPotentialRange = pot_outside
    assert ranging.StartPotentialRange.Description == '100 mV'

    # Check that max range gets clipped to nearest supported range
    ranging.MaximumPotentialRange = pot_outside
    assert ranging.MaximumPotentialRange.Description == '1 V'


def test_fixed_current_range():
    cr = '100uA'

    method = ps.CyclicVoltammetry(current_range=cr)

    assert isinstance(method.current_range, ps.settings.CurrentRange)
    assert method.current_range.min == cr
    assert method.current_range.max == cr
    assert method.current_range.start == cr


def test_fixed_potential_range():
    pr = '10mV'

    method = ps.ChronoPotentiometry(potential_range=pr)

    assert isinstance(method.potential_range, ps.settings.PotentialRange)
    assert method.potential_range.min == pr
    assert method.potential_range.max == pr
    assert method.potential_range.start == pr
