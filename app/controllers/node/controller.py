import os
import json
import copy
from controllers import log

def reconcile(state, config, *args):
    metadata = state.get('object',{}).get('metadata',{})
    annotations = metadata.get('annotations',{})
    labels = metadata.get('labels',{})
    name = metadata.get('name')
    uid = metadata.get('uid')
    node_taints = state.get('object',{}).get('spec',{}).get('taints', [])

    # copy label to annotation
    for prefix_name, value in labels.items():
        if not prefix_name.startswith('annotation.getup.io/'):
            continue
        _, name = prefix_name.split('/')
        if not name:
            continue
        log('Added annotation: {}={}'.format(name, value))
        annotations[name] = value

    # copy annotation to label
    for prefix_name, value in annotations.items():
        if not prefix_name.startswith('label.getup.io/'):
            continue
        _, name = prefix_name.split('/')
        if not name:
            continue
        log('Added label: {}={}'.format(name, value))
        labels[name] = value

    node_taints = reconcile_taints(labels, node_taints)
    node_taints = reconcile_taints(annotations, node_taints)

    state['object']['spec']['taints'] = node_taints
    state['object']['metadata']['annotations'] = annotations
    state['object']['metadata']['labels'] = labels

    return state

def reconcile_taints(source, node_taints=[]):
    '''Taints from labels or annotations
    Example for key=dedicated:
      taint.getup.io/dedicated.value: infra
      taint.getup.io/dedicated.effect: NoSchedule
      taint.getup.io/dedicated.operator: Exists
    '''
    node_taints = copy.deepcopy(node_taints)
    new_taints = {}
    default_effect = os.environ.get('DEFAULT_NODE_TAINT_EFFECT', 'NoSchedule')

    for prefix_name, value in source.items():
        if not prefix_name.startswith('taint.getup.io/'):
            continue
        _, tmp = prefix_name.split('/')
        key, field = tmp.split('.')

        if key not in new_taints:
            new_taints[key] = {'key': key}

        new_taints[key][field] = value

    taints_to_add = []
    for new_taint in new_taints.values():
        found = False
        for node_taint in node_taints:
            if node_taint == new_taint:
                log('Already exists taint: {}'.format(new_taint))
                found = True
        if not found:
            taints_to_add.append(new_taint)

    for taint in taints_to_add:
        log('Adding taint: {}'.format(taint))
        node_taints.append(taint)

    return node_taints
