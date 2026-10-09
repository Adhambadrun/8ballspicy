#!/usr/bin/env python3
"""CI provenance with exact source commit, source tree, and local artifact hashes.

Provenance records what actually happened: the checked-out commit, the git tree
IDs of the source directories, the toolchain, and the hashes of every artifact
in `dist/`. If a tool is unavailable -- for example on a non-macOS runner such
as the release-integrity gate -- the field records that fact instead of failing
or inventing a value. A provenance record must never contain a guessed
toolchain.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIRS = ['MrSpicyUI', 'HostApp', 'tools']
APPLE_TOOLS = {
    'toolchain': ('xcodebuild', '-version'),
    'swift': ('swift', '--version'),
    'os': ('sw_vers',),
    'sdk': ('xcrun', '--sdk', 'iphoneos', '--show-sdk-version'),
}


def run(argv, cwd=None):
    proc = subprocess.run(list(argv), capture_output=True, text=True, cwd=cwd)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def command(*args, cwd=None):
    code, out, err = run(args, cwd=cwd)
    if code != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {err or out}")
    return out


def describe(args):
    """Run a tool, or report honestly that it is unavailable."""
    if shutil.which(args[0]) is None:
        return f'unavailable ({args[0]} not installed on this runner)'
    try:
        return command(*args)
    except RuntimeError as exc:
        return f'unavailable ({exc})'


def require_env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f'{name} is not set; provenance requires a GitHub Actions environment')
    return value


def provenance(job):
    source = require_env('GITHUB_SHA')
    # `dist/` is job-relative (the component job runs inside MrSpicyUI/), exactly
    # as before; git commands inherit the working directory.
    dist = Path('dist')
    data = {
        'source_commit': source,
        'checked_out_commit': command('git', 'rev-parse', 'HEAD'),
        'run_id': int(require_env('GITHUB_RUN_ID')),
        'run_attempt': require_env('GITHUB_RUN_ATTEMPT'),
        'job': job,
        'ref': require_env('GITHUB_REF'),
        'source_trees': {p: command('git', 'rev-parse', f'{source}:{p}')
                         for p in SOURCE_DIRS},
        'toolchain': describe(APPLE_TOOLS['toolchain']),
        'swift': describe(APPLE_TOOLS['swift']),
        'os': describe(APPLE_TOOLS['os']),
        'sdk': describe(APPLE_TOOLS['sdk']),
        'component_signing': 'CODE_SIGNING_ALLOWED=NO; not installable',
        'artifacts': [],
    }
    if data['checked_out_commit'] != source:
        raise RuntimeError('checkout does not match workflow source')
    for p in sorted(dist.glob('*.zip')) if dist.exists() else []:
        data['artifacts'].append({
            'path': str(p),
            'size_bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        })
    return data


def main():
    job = sys.argv[1] if len(sys.argv) > 1 else 'unknown'
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('provenance.json')
    data = provenance(job)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({k: data[k] for k in ('job', 'source_commit', 'run_id')}, indent=2))


if __name__ == '__main__':
    main()
