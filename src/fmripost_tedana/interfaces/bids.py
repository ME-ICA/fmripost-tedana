"""BIDS-related interfaces for fMRIPost-template."""

from json import loads

from bids.layout import Config
from niworkflows.interfaces.bids import DerivativesDataSink as BaseDerivativesDataSink

from fmripost_tedana.data import load as load_data

# NOTE: Modified for fmripost_tedana's purposes
fmripost_tedana_spec = loads(load_data('io_spec.json').read_text())
bids_config = Config.load('bids')
deriv_config = Config.load('derivatives')

fmripost_tedana_entities = {v['name']: v['pattern'] for v in fmripost_template_spec['entities']}
merged_entities = {**bids_config.entities, **deriv_config.entities}
merged_entities = {k: v.pattern for k, v in merged_entities.items()}
merged_entities = {**merged_entities, **fmripost_tedana_entities}
merged_entities = [{'name': k, 'pattern': v} for k, v in merged_entities.items()]
config_entities = frozenset({e['name'] for e in merged_entities})


class DerivativesDataSink(BaseDerivativesDataSink):
    """Store derivative files.

    A child class of the niworkflows DerivativesDataSink,
    using fmripost_tedana's configuration files.
    """

    out_path_base = ''
    _allowed_entities = set(config_entities)
    _config_entities = config_entities
    _config_entities_dict = merged_entities
    _file_patterns = fmripost_tedana_spec['default_path_patterns']
