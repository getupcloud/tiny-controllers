import os
import sys
import yaml
import importlib
import subprocess

def log(*vargs, **kwargs):
    print(file=sys.stderr, *vargs, **kwargs)


def load_config(controller_name=None, controller_type=None, config_file=None):
    config = {}
    if config_file is None:
        config_file = os.environ.get("CONTROLLER_CONFIG_{}".format(controller_name.upper()), "/config/{}-{}.yaml".format(controller_name, controller_type))

    try:
        with open(config_file, 'r') as cf:
            log("Loading config file:", config_file)
            config = yaml.safe_load(cf)
    except FileNotFoundError as ex:
        pass
    except Exception as ex:
        log("Error loading config[%s:%s]: %s: %s" % (controller_name, controller_type, config_file, str(ex)))
        sys.exit(1)

    return config


def load_controller(controller_name, controller_type):
    controller = importlib.import_module('controllers.{}'.format(controller_name))
    func = getattr(controller, controller_type, None)
    return controller, func


def execute_command(args, stdin_data=''):
    #log(f"execute_command: echo '{stdin_data}' |", ' '.join([ f"'{i}'" for i in args]))
    result = subprocess.run(args=args, input=stdin_data, text=True, capture_output=True)

    if result.returncode == 0:
        return result.stdout

    log('Error: execute_command:', result.stderr)
