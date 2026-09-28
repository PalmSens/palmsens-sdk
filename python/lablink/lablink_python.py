from __future__ import annotations

import json
import time

import numpy as np
import requests
from signalrcore import hub_connection_builder

import pypalmsens as ps

if True:
    from PalmSens.Sdk.Lablink.Example.Lablink.Mappers import MethodMappers


addr = 'http://127.0.0.1:5000/api/v1/Home/GetInfo'

r = requests.get(addr)

# print(r.text)

r = requests.post(
    'http://localhost:5000/api/v1/Auth/ApiKey', json={'UserName': 'test', 'Password': 'test'}
)

j = json.loads(r.text)

token = j['Token']

headers = {'Authorization': f'Bearer {token}', 'accept': '*/*'}

hub = (
    hub_connection_builder.HubConnectionBuilder()
    .with_url(
        'http://localhost:5000/hub?InstrumentID=ES4LR20B0008', options={'headers': headers}
    )
    # .configure_logging(logging.INFO)
    .with_automatic_reconnect(
        {'type': 'raw', 'keep_alive_interval': 10, 'reconnect_interval': 5, 'max_attempts': 5}
    )
    .build()
)
# Events
# - "ReceiveMeasurementStarted"
# - "ReceiveMeasurementFinished"
# - "ReceiveMeasurementAborted"
# - "ReceiveMeasurementPaused"
# - "ReceiveDataSetStarted"
# - "ReceiveData"

hub.start()

finished = False


def callback(x, event):
    print(f' > event: {event} - {x}')


def callback_measurement_finished(x):
    global finished
    finished = True


hub.on('ReceiveMeasurementStarted', lambda x: callback(x, event='ReceiveMeasurementStarted'))
hub.on('ReceiveMeasurementFinished', lambda x: callback(x, event='ReceiveMeasurementFinished'))
hub.on('ReceiveMeasurementFinished', callback_measurement_finished)
hub.on('ReceiveMeasurementAborted', lambda x: callback(x, event='ReceiveMeasurementAborted'))
hub.on('ReceiveMeasurementPaused', lambda x: callback(x, event='ReceiveMeasurementPaused'))
hub.on('ReceiveDataSetStarted', lambda x: callback(x, event='ReceiveDataSetStarted'))
hub.on('ReceiveData', lambda x: callback(x, event='ReceiveData'))


# print(headers)

r = requests.get('http://localhost:5000/api/v1/Instruments', headers=headers)
r.raise_for_status()
# print(r.text[0:100])

r = requests.get('http://localhost:5000/api/v1/Measurements', headers=headers)
r.raise_for_status()
# print(r.text[0:100])

method = ps.MultiStepAmperometry()
dto = MethodMappers.ToDto(method._to_psmethod())

method2 = MethodMappers.FromDto(dto)  # revert to to 5.13 method

payload = {
    'Technique': dto.Technique,
    'MethodParameters': dict(dto.Parameters),
    'AllInstrumentsMUstSucceed': True,
    'InstrumentProperties': {'ES4LR20B0008': {}},
}

r = requests.post(
    'http://localhost:5000/api/v1/Instruments/StartMeasurement', json=payload, headers=headers
)
r.raise_for_status()
if not r.status_code == 200:
    raise ValueError(r.json()[0]['exceptionMessage']['resourceKey'])
# print(r.text)

id = r.json()[0]['result']


while not finished:
    time.sleep(1)

r = requests.get(
    f'http://localhost:5000/api/v1/Measurements/{id}', json=payload, headers=headers
)
r.raise_for_status()
print(r)

response = r.json()

dataset, *_ = response['RawDataSets']
dataset_id = dataset['DataSetId']

print()

for array in dataset['DataArrays']:
    array_type = array['DataValueType']
    print(array_type)
    array_id = array['DataArrayId']
    values_id = array['DataValuesId']
    r = requests.get(
        f'http://localhost:5000/api/v1/DataSets/{dataset_id}/{values_id}',
        headers=headers,
        stream=True,
    )
    r.raise_for_status()
    raw = r.content

    if array_type == 'CurrentRange':
        pairs = np.frombuffer(raw, dtype=np.int32).reshape(-1, 2)
        data = pairs[:, 0]
        other = pairs[:, 0]  # ?? factor? exponent?

    elif array_type in (
        'AppliedPotential',
        'Charge',
        'MeasuredCurrent',
        'AuxiliaryPotential',
        'ReverseCurrent',
        'ForwardCurrent',
    ):
        data = np.frombuffer(raw, dtype=np.float64)  # little-endian float64

    elif array_type in (
        'TimingStatus',
        'CurrentReadingStatus',
        'ForwardCurrentReadingStatus',
        'ReverseCurrentReadingStatus',
    ):
        data = np.frombuffer(raw, dtype=np.int8)  # int enum (8-bit signed integer)

    elif array_type in ('Index', 'CycleIndex', 'LevelIndex'):
        data = np.frombuffer(raw, dtype=np.int32)  # int enum (32 bit signed)

    elif array_type == 'Timestamp':
        ticks = np.frombuffer(raw, dtype=np.int64)  # 100-ns ticks
        data = ticks * 1e-7  # seconds

    else:
        print(len(r.content))
        print(r.content[:32].hex())
        data = '???'

    print(data, len(data))
    print()
