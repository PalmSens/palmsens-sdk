class EISFitResult:
    def __init__(self, cdc, values):
        self.cdc = cdc
        self.values = self.__convert_values(values)

    def __convert_values(self, values):
        converted_values = []
        if values is not None:
            for value in values:
                converted_values.append(value)
        return converted_values
