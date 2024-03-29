import os
import json
import copy
from controllers import log


annotation_prefix = 'annotation.getup.io.'
label_prefix = 'label.getup.io.'
taint_prefix = 'taint.getup.io.'


def reconcile(state, config, *args):
    metadata = state.get('object',{}).get('metadata',{})
    annotations = metadata.get('annotations',{})
    labels = metadata.get('labels',{})
    name = metadata.get('name')
    uid = metadata.get('uid')
    node_taints = state.get('object',{}).get('spec',{}).get('taints', [])
    changed = False

    # copy label to annotation
    for name, value in labels.items():
        if not name.startswith(annotation_prefix):
            continue
        name = name[len(annotation_prefix):]
        if not name:
            continue
        log('Added annotation: {}={}', name, value)
        annotations[name] = value
        changed = True

    # copy annotation to label
    for name, value in annotations.items():
        if not name.startswith(label_prefix):
            continue
        name = name[len(label_prefix):]
        if not name:
            continue
        log('Added label: {}={}', name, value)
        labels[name] = value
        changed = True

    # copy taints from labels and annotations
    new_taints = copy.deepcopy(node_taints)
    new_taints = reconcile_taints(labels, new_taints)
    new_taints = reconcile_taints(annotations, new_taints)

    if new_taints != node_taints:
        changed = True

    if not changed:
        return

    state['object']['spec']['taints'] = new_taints
    state['object']['metadata']['annotations'] = annotations
    state['object']['metadata']['labels'] = labels

    return state


def reconcile_taints(source, node_taints):
    '''Taints from labels or annotations
    Example for key=dedicated:
      taint.getup.io.dedicated.value: infra
      taint.getup.io.dedicated.effect: NoSchedule
      taint.getup.io.dedicated.operator: Exists
    '''
    node_taints = copy.deepcopy(node_taints)
    new_taints = {}
    default_effect = os.environ.get('DEFAULT_NODE_TAINT_EFFECT', 'NoSchedule')

    # read all taints from source
    for name, value in source.items():
        if not name.startswith(taint_prefix):
            continue
        tmp = name[len(taint_prefix):]
        key, field = tmp.split('.')

        if key not in new_taints:
            new_taints[key] = {'key': key}

        new_taints[key][field] = value

    # filter for taints to add to node
    taints_to_add = []
    for new_taint in new_taints.values():
        found = False

        if 'effect' not in new_taint:
            new_taint['effect'] = default_effect

        for node_taint in node_taints:
            if equal_taints(node_taint, new_taint):
                log('Already exists taint: {}', new_taint)
                found = True

        if not found:
            taints_to_add.append(new_taint)

    # add filtered taints
    for taint in taints_to_add:
        log('Adding taint: {}', taint)
        node_taints.append(taint)

    return node_taints


def equal_taints(a, b):
    eq = False
    try:
        eq = a['key'] == b['key'] and a['effect'] == b['effect']
    except KeyError:
        pass
    return eq


def init(config, controller_config):
    pass
