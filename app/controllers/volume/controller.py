import os
import json
import copy
from controllers import log
import itertools

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
    pv_annotations = pv_metadata.get('annotations', {})
    pv_labels = pv_metadata.get('labels', {})

    def copy_from(target, prefix_name, value):
        _, name = prefix_name.split('/', 1)
        if name:
            what = prefix_name.split('.')[1]
            log('Added {}: {}={}'.format(what, name, value))
            target[name] = value
        return target

    # copy pvc labels or annotations to pv
    for prefix_name, value in itertools.chain(pvc_labels.items(), pvc_annotations.items()):
        if prefix_name.startswith('pv.annotation.getup.io/'):
            pv_annotations = copy_from(pv_annotations, prefix_name, value)
        elif prefix_name.startswith('pv.label.getup.io/'):
            pv_labels = copy_from(pv_labels, prefix_name, value)
        else:
            changed = False

    state['object']['metadata']['annotations'] = pv_annotations
    state['object']['metadata']['labels'] = pv_labels

    return state


def init(config, controller_config):
    pass
