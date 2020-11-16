#!/usr/bin/env python

import os
import sys
import yaml
from controllers import log, load_config, load_controller


def init(config_file):
    config = load_config(config_file=config_file)

    for resource in config['resources']:
        try:
            controller_name, controller_type = resource['reconciler']['exec']['args']
        except (IndexError, KeyError) as ex:
            continue

        controller, init = load_controller(controller_name, 'init')

        if init is not None:
            log('Initializing {}'.format(controller.__name__))
            controller_config = load_config(controller_name=controller_name, controller_type=controller_type)
            init(config, controller_config)

if __name__ == '__main__':
    init(sys.argv[1])
