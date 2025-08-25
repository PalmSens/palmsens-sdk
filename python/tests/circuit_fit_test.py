from __future__ import annotations

import pytest
from numpy.testing import assert_allclose
from PalmSens import Fitting as PSFitting

from pypalmsens.fitting import CircuitModel, Parameter, Parameters


def test_parameter_slots():
    param = Parameter(symbol='R 1', value=123, min=0, max=1000, fixed=False)

    param.value = 1337

    with pytest.raises(AttributeError):
        param.i_do_not_exist = ...


def test_parameters():
    cdc = 'R(RC)'

    params = Parameters(cdc)

    assert len(params) == 3
    assert [prm.symbol for prm in params] == ['R 1', 'R 2', 'C 1']
    assert str(params)
    assert repr(params)

    psmodel = PSFitting.Models.CircuitModel()
    psmodel.SetCircuit(cdc)

    params[0].value = 123
    params[0].fixed = True
    params[1].min = 12
    params[1].max = 34

    params._update_psmodel_parameters(psmodel)
    psparams = psmodel.InitialParameters

    assert psparams[0].Value == 123
    assert psparams[0].Fixed is True
    assert psparams[1].MinValue == 12
    assert psparams[1].MaxValue == 34

    assert len(params) == 3


def test_default_parameters():
    cdc = 'R(RC)'
    model = CircuitModel(cdc)

    params = model.default_parameters()
    assert params.cdc == cdc
    assert len(params) == 3


def test_circuit_fit(data_eis_5freq):
    eis_data = data_eis_5freq[0].eis_data[0]
    cdc = 'R(RC)'
    model = CircuitModel(cdc=cdc)
    result = model.fit(eis_data)

    assert result.n_iter <= 10
    assert result.exit_code == 'MinimumDeltaErrorTerm'

    assert len(result.get_nyquist(data=eis_data)) == 2
    assert len(result.get_bode_z(data=eis_data)) == 2
    assert len(result.get_bode_phase(data=eis_data)) == 2

    assert_allclose(result.parameters, [564, 10077, 3.3275e-08], rtol=2e-3)
    assert_allclose(result.error, [1.471, 1.541, 1.925], rtol=1e-3)
    assert result.chisq < 0.0005
    assert result.cdc == cdc

    result2 = model.fit(eis_data, parameters=result.parameters)

    assert result2.n_iter <= 3

    parameters = model.default_parameters()

    for parameter in parameters:
        parameter.min = 123

    result3 = model.fit(eis_data, parameters=parameters)

    assert min(result3.parameters) >= 123
