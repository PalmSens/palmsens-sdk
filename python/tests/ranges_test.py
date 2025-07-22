import pytest
from PalmSens import AutoRanging, AutoRangingPotential

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
