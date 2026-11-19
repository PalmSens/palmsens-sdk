from __future__ import annotations

import pytest

import pypalmsens as ps


@pytest.mark.parametrize(
    'cls',
    [
        ps.corrosion.CorrosionPotential,
        ps.corrosion.CyclicPolarization,
        ps.corrosion.Galvanostatic,
        ps.corrosion.LinearPolarization,
        ps.corrosion.Potentiostatic,
        ps.corrosion.ImpedanceSpectroscopy,
    ],
)
def test_settings(cls):
    method = cls()

    assert method.material
