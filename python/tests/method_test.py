import pytest


@pytest.fixture
def method(data_cv_1scan):
    return data_cv_1scan[0].method


def test_properties(method):
    assert isinstance(repr(method), str)
    assert method.id == 'cv'
    assert method.name == 'Cyclic Voltammetry'
    assert method.short_name == 'CV'


def test_to_dict(method):
    dct = method.to_dict()
    assert dct

    # Skip because they return objects
    # that are not wrapped yet
    SKIP = (
        'bipot_ranging',
        'poly_em_stat',
        'ranging',
        'ranging_potential',
        'se_2_vs_x_channel',
    )

    for k, v in dct.items():
        if k in SKIP:
            continue
        assert isinstance(v, (int, float, list, dict, str, type(None))), f'{k=}:{v=}'
