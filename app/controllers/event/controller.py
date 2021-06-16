#!/usr/bin/env python

from __future__ import print_function
from controllers import log

def reconcile(state, config, *args):
    try:
        log(json.dumps(state.get('object')))
    except:
        log(state.get('object'))


def init(config, controller_config):
    pass
