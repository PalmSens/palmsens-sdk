import pypalmsens as ps

if True:
    import System
    from PalmSens.Core.Domain.Mappers import TechniqueParametersMappers
    from PalmSens.Sdk.Data.Extensions.Method import MethodExtensions


def convert(method):
    psmethod = method._to_psmethod()
    psmethod_new = MethodExtensions.ToMethodParameters(psmethod).__implementation__
    entity = TechniqueParametersMappers.ToEntity(psmethod_new)

    createdOn = System.DateTimeOffset.UtcNow

    entity.InitializeTimestamps(createdOn)
    # entity.AddParameter("Name", 'new name')
    # entity.AddNotesParameter('lorem ipsum')
    # entity.AddLabelsParameter([])
    # entity.AddCurveTemplatesParameter([])

    # generate d directly from method?
    parameters = {_.Key: _.Value for _ in entity.Parameters}
    parameters['Name'] = f'["{psmethod.Name}"]'

    return parameters


method = ps.ChronoAmperometry(run_time=1)
method.record_auxiliary_input = True
method.record_cell_potential = True
method.record_we_potential = True
method.enable_bipot_current = False  # not supported

method.ir_drop_compensation.resistance = 10

e = method._to_lablink_parameters()

parameters = convert(method)

import json

for k, v in parameters.items():
    parameters[k] = json.loads(v)


import deepdiff

ret = deepdiff.DeepDiff(parameters, e)

print(ret)


# dto = dict(MethodMappers.ToDto(method._to_psmethod()))
