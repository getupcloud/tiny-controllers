import os
import json
import copy
from controllers import log
import itertools


annotation_prefix = 'pv.annotation.getup.io.'
label_prefix = 'pv.label.getup.io.'


def reconcile(state, config, *args):
    pvcs = state.get('references', {}).get('persistentvolumeclaim.v1')

    if not pvcs:
        return

    pvc = pvcs[0]
    pvc_metadata = pvc.get('metadata', {})
    pvc_annotations = pvc_metadata.get('annotations', {})
    pvc_labels = pvc_metadata.get('labels', {})

    pv = state.get('object')
    pv_metadata = pv.get('metadata', {})
    pv_annotations = copy.deepcopy(pv_metadata.get('annotations', {}))
    pv_labels = copy.deepcopy(pv_metadata.get('labels', {}))

    def update(target, prefix, name, value):
        name = name[len(prefix):]
        if name:
            what = prefix.split('.')[1]
            log('Added {}: {}={}', what, name, value)
            target[name] = value
        return target

    # copy pvc labels or annotations to pv
    for name, value in itertools.chain(pvc_labels.items(), pvc_annotations.items()):
        if name.startswith(annotation_prefix):
            pv_annotations = update(pv_annotations, annotation_prefix, name, value)
        elif name.startswith(label_prefix):
            pv_labels = update(pv_labels, label_prefix, name, value)

    state['object']['metadata']['annotations'] = pv_annotations
    state['object']['metadata']['labels'] = pv_labels

    return state


def init(config, controller_config):
    pass
