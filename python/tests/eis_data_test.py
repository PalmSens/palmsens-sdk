from __future__ import annotations

import pytest


@pytest.fixture
def eis_simple(data_eis_5freq):
    return data_eis_5freq[0].eis_data


@pytest.fixture
def eis_mux_subscans(data_eis_3ch_4scan_5freq):
    return data_eis_3ch_4scan_5freq[0].eis_data


def test_eis_data(eis_simple):
    assert len(eis_simple) == 1
    eis = eis_simple[0]

    assert str(eis)

    assert not eis.has_subscans
    assert eis.n_subscans == 0

    assert eis.scan_type == 'Fixed'
    assert eis.frequency_type == 'Scan'
    assert eis.n_points == 5
    assert eis.n_frequencies == 5

    assert eis.x_quantity == 'Time'
    assert eis.x_unit == 's'

    assert eis.current_range() == ['10 mA', '1 mA', '100 uA', '10 uA', '1 uA']

    lst = eis.arrays()
    assert len(lst) == 18


def test_eis_dataset(eis_simple):
    dataset = eis_simple[0].dataset

    assert dataset.current_range() == ['10 mA', '1 mA', '100 uA', '10 uA', '1 uA']
    assert dataset.reading_status() == ['Underload'] * 4 + ['OK']

    assert len(dataset) == 18


def test_eis_data_mux_subscans(eis_mux_subscans):
    assert len(eis_mux_subscans) == 3  # 3 mux channels

    eis = eis_mux_subscans[0]

    assert str(eis)

    assert eis.has_subscans
    assert eis.n_subscans == 4

    assert eis.scan_type == 'PGScan'
    assert eis.frequency_type == 'Scan'
    assert eis.n_points == 20
    assert eis.n_frequencies == 5

    assert eis.x_quantity == 'Potential'
    assert eis.x_unit == 'V'

    assert set(eis.current_range()) == {'10 mA', '1 mA', '100 uA', '10 uA', '1 uA'}

    assert len(eis.subscans) == 4

    lst = eis.arrays()
    assert len(lst) == 18


def test_eis_data_mux_subscans_dataset(eis_mux_subscans):
    assert len(eis_mux_subscans) == 3  # 3 mux channels

    dataset = eis_mux_subscans[0].dataset

    assert set(dataset.current_range()) == {'10 mA', '1 mA', '100 uA', '10 uA', '1 uA'}
    assert set(dataset.reading_status()) == {'Underload', 'OK'}

    assert len(dataset) == 18
