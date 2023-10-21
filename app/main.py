#!/usr/bin/env python

import sys
import json
import logging
from controllers import log, load_config, load_controller


if __name__ == "__main__":
    try:
        controller_name, controller_type, *args = *sys.argv[1:3], *sys.argv[3:]
    except ValueError as ex:
        log("Invalid parameters: Usage: %s [controller-name] [controller-type]" % sys.argv[0])
        log("Invalid parameters: Got %s" % sys.argv)
        sys.exit(1)

    try:
        controller, func = load_controller(controller_name, controller_type)
        config = load_config(controller_name=controller_name, controller_type=controller_type)
        state = json.load(sys.stdin)

        result = func(state, config, *args)

        if result is not None:
            log(result)

        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as e:
        log("Error executing controller: %s:%s" % (controller_name, controller_type))
        logging.exception("%s", e)
        sys.exit(1)
