#!/usr/bin/env python3
"""Verify fetched CI evidence: ZIP bytes, ARM64 MH_OBJECT, counts and source trees."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import zipfile
from pathlib import Path


def tests(path):
    text = path.read_text()
    outcomes = re.findall(r"^Test Case '(.+)' (passed|failed|skipped) \(", text, re.M)
    counts = {k: sum(status == k for _,status in outcomes) for k in ('passed','failed','skipped')}
    counts['executed'] = len(outcomes)
    counts['cases'] = [{'name': n, 'status':s} for n,s in outcomes]
    counts['test_succeeded_marker'] = '** TEST SUCCEEDED **' in text
    counts['warnings'] = [line for line in text.splitlines() if 'warning:' in line]
    counts['errors'] = [line for line in text.splitlines() if 'error:' in line]
    if not outcomes:
        raise ValueError(f'no XCTest cases in {path}')
    return counts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=int)
    p.add_argument('--root',type=Path,default=Path('validation/ci/runs'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    component=a.root/f'{a.run}-component'
    hosted=a.root/f'{a.run}-hosted-tests'
    prov=json.loads((component/'provenance.json').read_text())
    hprov=json.loads((hosted/'provenance.json').read_text())
    if prov['source_commit'] != hprov['source_commit'] or prov['source_commit'] != prov['checked_out_commit']:
        raise ValueError('source provenance mismatch')
    source=prov['source_commit']
    for tree,oid in prov['source_trees'].items():
        observed=subprocess.check_output(['git','rev-parse',f'{source}:{tree}'],text=True).strip()
        if observed != oid:
            raise ValueError('source tree mismatch: '+tree)
    package=component/'dist/MrSpicyUI-iphoneos-arm64-unsigned.zip'
    sha=hashlib.sha256(package.read_bytes()).hexdigest()
    if prov['artifacts'][0]['sha256'] != sha or package.stat().st_size != prov['artifacts'][0]['size_bytes']:
        raise ValueError('artifact provenance hash/size mismatch')
    with zipfile.ZipFile(package) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failed')
        obj=z.read('MrSpicyUI.o')
        header=struct.unpack_from('<8I',obj)
        if header[0] != 0xfeedfacf or header[1] != 0x100000c or header[3] != 1:
            raise ValueError('expected thin arm64 MH_OBJECT, not application')
        entries=[{'path':i.filename,'size_bytes':i.file_size} for i in z.infolist()]
    out={'run_id':a.run,'source_commit':source,'source_trees':prov['source_trees'],
         'artifact':{'path':str(package),'size_bytes':package.stat().st_size,'sha256':sha,'zip_crc':'PASS',
                     'mach_o':'arm64 thin MH_OBJECT (relocatable component, not app)',
                     'object_sha256':hashlib.sha256(obj).hexdigest(),'object_size_bytes':len(obj),'signed':False,'contents':entries},
         'provenance':prov,'tests':{'hostless':tests(component/'xcodebuild-test.log'),
                                  'hosted':tests(hosted/'xcodebuild-hosted.log')},
         'device_build_succeeded': '** BUILD SUCCEEDED **' in (component/'xcodebuild-device.log').read_text(),
         'apple_input_verification':(component/'input-apple-verification.txt').read_text() if (component/'input-apple-verification.txt').exists() else 'NOT RUN in this revision'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:out[k] for k in ('run_id','source_commit','device_build_succeeded')},indent=2))
    print(json.dumps({k:{key:v[key] for key in ('passed','failed','skipped','executed')} for k,v in out['tests'].items()},indent=2))
    print(sha,str(package))


if __name__=='__main__':
    main()
