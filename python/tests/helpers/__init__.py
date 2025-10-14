from __future__ import annotations


def assert_params_match_kwargs(params, *, kwargs):
    for key, exp in kwargs.items():
        ret = getattr(params, key)
        assert ret == exp
