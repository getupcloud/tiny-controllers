import os
import sys
import yaml
import importlib
import subprocess

def log(*vargs, **kwargs):
    print(file=sys.stderr, *vargs, **kwargs)


def load_config(controller_name=None, controller_type=None, config_file=None):
    final_config_file = None

    if controller_name and controller_type:
        final_config_file = "/config/{}-{}.yaml".format(controller_name, controller_type)

    if config_file:
        final_config_file = config_file

    if "CONTROLLER_CONFIG" in os.environ:
        final_config_file = os.environ.get("CONTROLLER_CONFIG")

    if controller_name:
        final_config_file = os.environ.get("CONTROLLER_CONFIG_{}".format(controller_name.upper()))

    log("Loading config file:", final_config_file)
    try:
        if final_config_file:
            with open(final_config_file, 'r') as fp:
                return yaml.safe_load(fp)
    except FileNotFoundError as ex:
        pass
    except Exception as ex:
        log("Error loading config[%s:%s]: %s: %s" % (controller_name, controller_type, final_config_file, str(ex)))
        sys.exit(1)

    return {}


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
