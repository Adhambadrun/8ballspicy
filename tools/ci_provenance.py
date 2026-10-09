#!/usr/bin/env python3
"""CI provenance with exact source commit, source tree, and local artifact hashes."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def command(*args):
    return subprocess.check_output(args, text=True).strip()


root = Path(os.environ['GITHUB_WORKSPACE'])
source = os.environ['GITHUB_SHA']
data = {'source_commit': source, 'checked_out_commit': command('git', 'rev-parse', 'HEAD'),
        'run_id': int(os.environ['GITHUB_RUN_ID']), 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'job': sys.argv[1], 'ref': os.environ['GITHUB_REF'],
        'source_trees': {p: command('git', 'rev-parse', f'{source}:{p}') for p in ['MrSpicyUI', 'HostApp', 'tools']},
        'toolchain': command('xcodebuild', '-version'), 'swift': command('swift', '--version'),
        'os': command('sw_vers'), 'sdk': command('xcrun', '--sdk', 'iphoneos', '--show-sdk-version'),
        'component_signing': 'CODE_SIGNING_ALLOWED=NO; not installable', 'artifacts': []}
if data['checked_out_commit'] != source:
    raise RuntimeError('checkout does not match workflow source')
for p in sorted(Path('dist').glob('*.zip')):
    data['artifacts'].append({'path': str(p), 'size_bytes': p.stat().st_size,
                              'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
Path(sys.argv[2]).write_text(json.dumps(data, indent=2)+'\n')
