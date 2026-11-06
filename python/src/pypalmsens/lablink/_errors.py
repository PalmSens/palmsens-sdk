"""Lablink API error handling."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_WORD_BOUNDARY = re.compile(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')


def humanize(resource_key: str) -> str:
    """Generate readable messages from a resource key.

    'Conflict__InstrumentNoActiveMeasurement' -> 'Instrument no active measurement.'
    """
    _, name = resource_key.split('__')
    words = _WORD_BOUNDARY.sub(' ', name or resource_key).split()
    sentence = ' '.join(words)
    return sentence[0].upper() + sentence[1:] + '.'


class LablinkApiError(ConnectionError):
    """Base class for errors returned by the Lablink API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        resource_key: str | None = None,
        dictionary: str | None = None,
        serial: str | None = None,
        parameters: list[Any] | None = None,
        response: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.resource_key = resource_key
        self.dictionary = dictionary
        self.serial = serial
        self.parameters = parameters or []
        self.response = response


class NoActiveMeasurementError(LablinkApiError):
    """The instrument has no active measurement."""


class LablinkClientError(LablinkApiError):
    """4xx client error."""


class LablinkServerError(LablinkApiError):
    """5xx server error."""


_CUSTOM_MESSAGES: dict[str, str] = {
    'Conflict__InstrumentNoActiveMeasurement': 'The instrument has no active measurement.',
}

_EXCEPTION_MAPPING: dict[str, type[LablinkApiError]] = {
    'Conflict__InstrumentNoActiveMeasurement': NoActiveMeasurementError,
}


def build_error(data: Mapping[str, Any]) -> LablinkApiError:
    exc = data.get('exceptionMessage', {})
    key = exc.get('resourceKey')
    status_code = data.get('statusCode')
    dictionary = exc.get('resourceDictionaryName') or ''
    _, _, dictionary_name = dictionary.rpartition('.')

    if key and key in _EXCEPTION_MAPPING:
        cls = _EXCEPTION_MAPPING[key]

    elif status_code:
        if 400 <= status_code < 500:
            cls = LablinkClientError

        elif status_code >= 500:
            cls = LablinkServerError

        else:
            cls = LablinkApiError

    else:
        cls = LablinkApiError

    try:
        message = _CUSTOM_MESSAGES[key]
    except KeyError:
        message = humanize(key)

    params = exc.get('parameters')
    if params:
        message += f' ({", ".join(map(str, params))})'

    return cls(
        message,
        status_code=status_code,
        resource_key=key,
        dictionary=dictionary_name or None,
        serial=data.get('serial'),
        parameters=params,
        response=data,
    )
