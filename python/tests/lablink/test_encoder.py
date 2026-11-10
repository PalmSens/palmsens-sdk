import json

from pypalmsens.lablink.models._encoders import PlainFloatEncoder


def test_encoder():
    assert json.dumps(0.000001) == '1e-06'
    assert json.dumps(0.000001, cls=PlainFloatEncoder) == '0.000001'
    assert json.dumps(1e-6, cls=PlainFloatEncoder) == '0.000001'
    assert json.dumps(1e16) == '1e+16'
    assert json.dumps(1e16, cls=PlainFloatEncoder) == '10000000000000000'
    assert json.dumps(1e16, cls=PlainFloatEncoder) == '10000000000000000'
