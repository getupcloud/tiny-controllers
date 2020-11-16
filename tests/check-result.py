#!/usr/bin/env python

import sys
import json
from flatten_dict import flatten as _flatten

try:
    data = json.load(sys.stdin)['object']
except Exception as ex:
    print("Missing or invalid test data:", ex)
    sys.exit(1)

try:
    results = json.load(open(sys.argv[1], "r"))['results']
except Exception as ex:
    print("Missing or invalid test results:", ex)
    sys.exit(1)

def flatten(d):
    return _flatten(d, reducer='dot', keep_empty_types=(dict,), enumerate_types=(list,))

data = flatten(data)
ok = True

for r in [ flatten(i) for i in results ]:
    for k, v in r.items():
        if k not in data:
            print(f'{k} not found in {data}')
            ok = False
        elif v != data[k]:
            print(f'{k}={data[k]} do not matches {k}={v}')
            ok = False
        else:
            print(f"Match: {r}")

sys.exit(0 if ok else 1)
