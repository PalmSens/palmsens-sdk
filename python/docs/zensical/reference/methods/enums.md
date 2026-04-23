# Types

For type checking, PyPalmSens uses [Literal strings](https://mypy.readthedocs.io/en/stable/literal_types.html) to define the allowed settings, such as supported current and potential ranges.

::: pypalmsens.settings
    options:
      members_order: source
      members:
        - AllowedCurrentRanges
        - AllowedDeviceState
        - AllowedMethods
        - AllowedPotentialRanges
        - AllowedReadingStatus
        - AllowedTimingStatus
