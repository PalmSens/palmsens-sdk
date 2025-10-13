from __future__ import annotations

from pytest import approx


def assert_params_match_kwargs(params, *, kwargs):
    for key, exp in kwargs.items():
        ret = getattr(params, key)
        if isinstance(exp, float):
            assert ret == approx(exp)
        else:
            assert ret == exp
