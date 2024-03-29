import sys
#import yaml
import json
import copy
from controllers import log, execute_command


def command(args, obj):
    output = execute_command(args, stdin_data=json.dumps(obj))
    return json.loads(output) if output is not None else None

def reconcile(state, config, *args):
    obj = state['object']
    paths = config.get('paths', {})
    kubectl = paths.get('kubectl', 'kubectl')
    jq = paths.get('jq', 'jq')

    for patch in get_patches(obj, config, jq):
        if patch['type'] == 'jq':
            output = command([ jq, f'{patch["patch"]}' ], obj)
            if output is not None:
                state['object'] = output

        elif patch['type'] in ['json', 'merge', 'strategic']:
            if isinstance(patch['patch'], str):
                json_patch = patch['patch']
            else:
                json_patch = json.dumps(patch['patch'])
            args = [ f'{kubectl}', 'patch', '--output=json', '--dry-run', f'--type={patch["type"]}', '--filename=-', f"--patch={json_patch}" ]
            output = command(args, obj)
            if output is not None:
                state['object'] = output

        elif patch['type'] == 'python':
            exec(patch['patch'])

        obj = state['object']

    return state


def get_patches(obj, config, jq):
    kind = obj['kind']
    apiVersion = obj['apiVersion']
    name = obj['metadata']['name']
    namespace = obj['metadata'].get('namespace')

    for resource in config['resources']:
        if resource['kind'] == kind and resource['apiVersion'] == apiVersion:
            for patch in resource['patches']:
                if 'namespace' in patch and patch['namespace'] != namespace:
                    continue

                if 'name' in patch and patch['name'] != name:
                    continue

                ignore = False
                for match in patch.get('matches', []):
                    if not command([jq, '-r', match], obj):
                        log(f'PatchController: ignored {kind} {namespace}/{name} by non-matching condition: {match}')
                        ignore = True

                if ignore:
                    continue

                for spec in patch['specs']:
                    for patch_type, patch_value in spec.items():
                        if patch_value:
                            yield {
                                'type': patch_type,
                                'patch': patch_value
                            }


def init(config, controller_config):
    ## TODO: cehck for matching confog/controller_config resources
    pass
