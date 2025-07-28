import pytest
from PalmSens import AutoRanging, AutoRangingPotential

from pspython.methods import techniques
from pspython.methods._shared import get_current_range, get_potential_range


def test_current_range():
    assert get_current_range(0).ToString() == '100 pA'
    assert get_current_range(30).ToString() == '1 A'
    assert get_current_range(26).ToString() == '63 uA'

    with pytest.raises(ValueError):
        get_current_range(-1)
        get_current_range(100)


def test_potential_range():
    assert get_potential_range(0).ToString() == '1 mV'
    assert get_potential_range(4).ToString() == '100 mV'
    assert get_potential_range(7).ToString() == '1 V'

    with pytest.raises(ValueError):
        get_potential_range(-1)
        get_potential_range(100)


def test_method_current_range():
    crmin = get_current_range(3)
    crmax = get_current_range(7)
    crstart = get_current_range(6)

    method = techniques.CyclicVoltammetryParameters(
        current_range_min=crmin,
        current_range_max=crmax,
        current_range_start=crstart,
    )
    obj = method.to_psobj()

    supported_ranges = obj.Ranging.SupportedCurrentRanges

    assert crmin in supported_ranges
    assert crmax in supported_ranges
    assert crstart in supported_ranges

    assert obj.Ranging.MinimumCurrentRange.Description == '100 nA'
    assert obj.Ranging.MaximumCurrentRange.Description == '1 mA'
    assert obj.Ranging.StartCurrentRange.Description == '100 uA'


def test_method_potential_range():
    potmin = get_potential_range(0)
    potmax = get_potential_range(4)
    potstart = get_potential_range(1)

    method = techniques.ChronopotentiometryParameters(
        potential_range_min=potmin,
        potential_range_max=potmax,
        potential_range_start=potstart,
    )
    obj = method.to_psobj()
    supported_ranges = obj.RangingPotential.SupportedPotentialRanges

    assert potmin in supported_ranges
    assert potmax in supported_ranges
    assert potstart in supported_ranges

    assert obj.RangingPotential.MinimumPotentialRange.Description == '1 mV'
    assert obj.RangingPotential.MaximumPotentialRange.Description == '100 mV'
    assert obj.RangingPotential.StartPotentialRange.Description == '10 mV'


def test_method_current_range_clipping():
    ranging = AutoRanging(
        minRange=get_current_range(3),
        maxRange=get_current_range(7),
        startRange=get_current_range(6),
    )

    cr_outside = get_current_range(20)
    assert cr_outside not in ranging.SupportedCurrentRanges

    # Check that start range gets clipped to max range
    ranging.StartCurrentRange = cr_outside
    assert ranging.StartCurrentRange.Description == '1 mA'

    # Check that max range gets clipped to nearest supported range
    ranging.MaximumCurrentRange = cr_outside
    assert ranging.MaximumCurrentRange.Description == '10 mA'


def test_method_potential_range_clipping():
    ranging = AutoRangingPotential(
        minRange=get_potential_range(0),
        maxRange=get_potential_range(4),
        startRange=get_potential_range(1),
    )

    pot_outside = get_potential_range(6)
    assert pot_outside not in ranging.SupportedPotentialRanges

    # Check that start range gets clipped to max range
    ranging.StartPotentialRange = pot_outside
    assert ranging.StartPotentialRange.Description == '100 mV'

    # Check that max range gets clipped to nearest supported range
    ranging.MaximumPotentialRange = pot_outside
    assert ranging.MaximumPotentialRange.Description == '1 V'
