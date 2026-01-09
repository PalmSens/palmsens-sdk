from __future__ import annotations

import pytest

from pypalmsens._data.shared import ArrayType
from pypalmsens.data import DataArray


@pytest.fixture
def dataset(data_cv_1scan):
    return data_cv_1scan[0].dataset


def test_mapping(dataset):
    assert len(dataset) == 4
    assert len(dataset.keys()) == 4
    assert len(dataset.items()) == 4
    assert len(dataset.values()) == 4
    assert len([_ for _ in dataset]) == 4

    assert list(dataset) == [
        'Time',
        'Potential',
        'Current',
        'Charge',
    ]

    assert isinstance(repr(dataset), str)
    assert 'Time' in dataset
    assert isinstance(dataset['Time'], DataArray)

    assert 'foo' not in dataset
    with pytest.raises(KeyError):
        dataset['FAIL']


def test_to_list(dataset):
    lst = list(dataset.values())
    assert isinstance(lst, list)
    assert len(lst) == 4
    assert all(isinstance(item, DataArray) for item in lst)
    assert isinstance(dataset.arrays(), list)


def test_to_dict(dataset):
    dct = dict(dataset)
    assert isinstance(dct, dict)
    assert len(dct) == 4
    assert all(isinstance(item, DataArray) for item in dct.values())
    assert list(dct.keys()) == [
        'Time',
        'Potential',
        'Current',
        'Charge',
    ]


def test_list_arrays(dataset):
    assert len(dataset.current_arrays()[0]) == 41
    assert len(dataset.potential_arrays()[0]) == 41
    assert len(dataset.time_arrays()[0]) == 41

    assert len(dataset.freq_arrays()) == 0
    assert len(dataset.zre_arrays()) == 0
    assert len(dataset.zim_arrays()) == 0
    assert len(dataset.aux_input_arrays()) == 0


def test_array_types(dataset):
    types = dataset.array_types
    assert len(types) == 4
    assert types == {
        ArrayType.Time,
        ArrayType.Potential,
        ArrayType.Current,
        ArrayType.Charge,
    }


def test_array_names(dataset):
    names = dataset.array_names
    assert len(names) == 2
    assert names == {'time', 'scan1channel1'}


def test_new_curve(dataset):
    curve = dataset.curve(x='Time', y='Current')

    assert curve.title == 'Time-Current'
    assert len(curve) == 41


def test_array_quantities(dataset):
    quantities = dataset.array_quantities
    assert len(quantities) == 4
    assert quantities == {'Time', 'Potential', 'Current', 'Charge'}


def test_arrays_by_name(dataset):
    lst = dataset.arrays_by_name('scan1channel1')
    assert len(lst) == 3
    assert [item.quantity for item in lst] == ['Potential', 'Current', 'Charge']

    assert not dataset.arrays_by_name('FAIL')


def test_arrays_by_type(dataset):
    lst = dataset.arrays_by_type(ArrayType.Potential)
    assert len(lst) == 1
    assert lst[0].type.name == 'Potential'

    assert not dataset.arrays_by_type(ArrayType.Unspecified)


def test_arrays_by_quantity(dataset):
    lst = dataset.arrays_by_quantity('Potential')
    assert len(lst) == 1
    assert lst[0].quantity == 'Potential'

    assert not dataset.arrays_by_quantity('laitnetoP')
