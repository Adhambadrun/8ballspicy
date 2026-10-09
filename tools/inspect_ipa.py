#!/usr/bin/env python3
"""Read-only IPA inspection. No extraction/execution; emits metadata, not binaries.

CodeDirectory hash comparisons are structural integrity checks, NOT Apple's
codesign/CMS trust validation. Nonzero scatter tables are explicitly unsupported.
"""
import argparse
import collections
import hashlib
import json
import plistlib
import re
import struct
import zipfile
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def version(n):
    return f'{n >> 16}.{(n >> 8) & 255}.{n & 255}'


def macho(b, info=None, resources=None):
    if b[:4] != b'\xcf\xfa\xed\xfe':
        return {'format': 'unsupported (not thin little-endian Mach-O 64)'}
    h = struct.unpack_from('<8I', b)
    out = {'format': 'Mach-O 64-bit little-endian', 'cpu_type': h[1],
           'architecture': 'arm64' if h[1] == 0x100000c else str(h[1]),
           'file_type': h[3], 'load_command_count': h[4], 'flags': hex(h[6]),
           'sha256': digest(b), 'size_bytes': len(b), 'dependencies': [],
           'rpaths': [], 'encryption': [], 'sections': []}
    o = 32
    sig = None
    for _ in range(h[4]):
        cmd, size = struct.unpack_from('<II', b, o)
        if size < 8 or o + size > 32 + h[5] or o + size > len(b):
            raise ValueError('invalid load command bounds')
        if cmd in (0xc, 0x80000018, 0x8000001f, 0x80000023, 0x20, 0x8000001c):
            offset = struct.unpack_from('<I', b, o + 8)[0]
            name = b[o+offset:o+size].split(b'\0')[0].decode(errors='replace')
            out['rpaths' if cmd == 0x8000001c else 'dependencies'].append(name)
        elif cmd == 0x32:
            platform, minos, sdk = struct.unpack_from('<3I', b, o+8)
            out['build_version'] = {'platform': platform, 'minimum_os': version(minos), 'sdk': version(sdk)}
        elif cmd == 0x24 or cmd == 0x25:
            minos, sdk = struct.unpack_from('<2I', b, o+8)
            out['legacy_minimum_os'] = version(minos)
        elif cmd in (0x21, 0x2c):
            cryptoff, cryptsize, cryptid = struct.unpack_from('<3I', b, o+8)
            out['encryption'].append({'offset': cryptoff, 'size': cryptsize, 'crypt_id': cryptid})
        elif cmd == 0x1b:
            out['uuid_hex'] = b[o+8:o+24].hex()
        elif cmd == 0x1d:
            sig = struct.unpack_from('<2I', b, o+8)
        elif cmd == 0x19:
            nsects = struct.unpack_from('<I', b, o+64)[0]
            for i in range(nsects):
                so = o+72+i*80
                if so+80 > o+size:
                    raise ValueError('section outside command')
                sect, seg, addr, length, offset = struct.unpack_from('<16s16sQQI', b, so)
                out['sections'].append({'segment': seg.rstrip(b'\0').decode(), 'section': sect.rstrip(b'\0').decode(),
                                        'address': addr, 'size': length, 'file_offset': offset})
        elif cmd == 0x2:
            symoff, nsyms, stroff, strsize = struct.unpack_from('<4I', b, o+8)
            symbols = []
            counts = collections.Counter()
            for i in range(nsyms):
                ix, typ, sec, desc, value = struct.unpack_from('<IBBHQ', b, symoff+i*16)
                if typ & 0xe0 or ix >= strsize:
                    continue
                end = b.find(b'\0', stroff+ix, stroff+strsize)
                name = b[stroff+ix:end if end >= 0 else stroff+strsize].decode(errors='replace')
                kind = 'undefined' if typ & 0xe == 0 else 'defined_external' if typ & 1 else 'defined_local'
                counts[kind] += 1
                if any(s in name for s in ('UIApplication', 'UIViewController', 'dlopen', 'GBMenu', 'Spicy')):
                    symbols.append({'name': name, 'kind': kind})
            out['symbol_table'] = {'nsyms': nsyms, 'counts': dict(counts), 'selected_symbols': symbols[:100],
                                   'note': 'nlist symbols; not equivalent to export-trie counts or source code'}
        o += size
    out['code_signature'] = {'present': sig is not None, 'trust_verified': False}
    if sig:
        off, size = sig
        if off+size > len(b):
            raise ValueError('signature outside slice')
        magic, length, count = struct.unpack_from('>3I', b, off)
        if magic != 0xfade0cc0 or length > size:
            raise ValueError('unsupported/invalid signature SuperBlob')
        blobs = {}
        for i in range(count):
            slot, rel = struct.unpack_from('>2I', b, off+12+i*8)
            bm, bl = struct.unpack_from('>2I', b, off+rel)
            if rel+bl > length:
                raise ValueError('signature subblob outside SuperBlob')
            blobs[slot] = b[off+rel:off+rel+bl]
        s = out['code_signature']
        s.update({'offset': off, 'size': size, 'superblob_length': length,
                  'slots': [{'slot': hex(k), 'magic': hex(struct.unpack_from('>I', v)[0]), 'size': len(v)} for k,v in blobs.items()],
                  'code_directories': []})
        if 5 in blobs:
            s['entitlements'] = plistlib.loads(blobs[5][8:])
        for slot, cd in blobs.items():
            if struct.unpack_from('>I', cd)[0] != 0xfade0c02:
                continue
            ver, flags, ho, io, ns, nc, limit = struct.unpack_from('>7I', cd, 8)
            hs, ht, platform, ps = struct.unpack_from('>4B', cd, 36)
            scatter = struct.unpack_from('>I', cd, 44)[0] if ver >= 0x20100 else 0
            limit64 = struct.unpack_from('>Q', cd, 56)[0] if ver >= 0x20300 else 0
            limit = limit64 or limit
            d = {'slot': hex(slot), 'version': hex(ver), 'flags': hex(flags), 'identifier': cd[io:].split(b'\0')[0].decode(),
                 'code_limit': limit, 'signature_offset': off, 'hash_type': ht, 'hash_size': hs,
                 'page_exponent': ps, 'code_slots': nc, 'special_slots': ns, 'scatter_offset': scatter}
            s['code_directories'].append(d)
            hashname = {1: 'sha1', 2: 'sha256', 3: 'sha256', 4: 'sha384'}.get(ht)
            if scatter or not hashname or ps > 30 or ho-ns*hs < 0 or ho+nc*hs > len(cd):
                d['verification'] = 'NOT TESTED (unsupported format or invalid hash-table bounds)'
                continue
            page = 1 << ps if ps else limit
            d['expected_code_slots'] = (limit+page-1)//page if page else 0
            mismatches = []
            for i in range(nc):
                start, end = i*page, min((i+1)*page, limit)
                actual = hashlib.new(hashname, b[start:end]).digest()[:hs]
                if end > len(b) or actual != cd[ho+i*hs:ho+(i+1)*hs]:
                    mismatches.append(i)
            d['page_hash_mismatches'] = len(mismatches)
            d['first_mismatching_pages'] = mismatches[:12]
            d['mismatches_wholly_before_signature'] = sum((i+1)*page <= off for i in mismatches)
            d['mismatches_overlapping_signature'] = sum((i+1)*page > off for i in mismatches)
            d['pre_encrypt_offset'] = struct.unpack_from('>I', cd, 88)[0] if ver >= 0x20500 else 0
            d['team_identifier'] = cd[struct.unpack_from('>I', cd, 48)[0]:].split(b'\0')[0].decode(errors='replace') if ver >= 0x20200 and struct.unpack_from('>I', cd, 48)[0] else None
            d['code_limit_overlaps_signature'] = limit > off
            d['special_slot_checks'] = {}
            for k, data in {1: info, 2: blobs.get(2), 3: resources, 5: blobs.get(5), 7: blobs.get(7)}.items():
                if k > ns or data is None:
                    continue
                expected = cd[ho-k*hs:ho-(k-1)*hs]
                d['special_slot_checks'][str(k)] = 'MATCH' if hashlib.new(hashname,data).digest()[:hs] == expected else 'MISMATCH'
            d['verification'] = 'HASH MISMATCH' if mismatches or 'MISMATCH' in d['special_slot_checks'].values() else 'HASHES MATCH (not trust verification)'
    return out


def seal(z, base, names):
    path = base+'_CodeSignature/CodeResources'
    if path not in names:
        return None
    table = plistlib.loads(z.read(path)).get('files2', {})
    result = collections.Counter()
    anomalies = []
    for rel, item in table.items():
        p = base+rel
        if p not in names:
            result['missing_entries'] += 1
            anomalies.append({'path': rel, 'status': 'MISSING', 'optional': isinstance(item,dict) and bool(item.get('optional'))})
            continue
        checks = {'hash': 'sha1', 'hash2': 'sha256'} if isinstance(item,dict) else {'hash': 'sha1'}
        for key, alg in checks.items():
            expected = item.get(key) if isinstance(item,dict) else item
            if not isinstance(expected,bytes):
                continue
            ok = hashlib.new(alg,z.read(p)).digest() == expected
            result['matching_hashes' if ok else 'mismatching_hashes'] += 1
            if not ok:
                anomalies.append({'path': rel, 'algorithm': alg, 'status': 'MISMATCH'})
    return {'path': path, 'files2_entries': len(table), 'counts': dict(result), 'anomalies': anomalies,
            'note': 'Comparisons of declared file hashes only; nested-code seals/rules/CMS trust not validated.'}


def inspect(path):
    before = digest(path.read_bytes())
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        bad = z.testzip()
        if bad:
            raise ValueError('ZIP CRC failure: '+bad)
        roots = [n[:-10] for n in names if n.endswith('/Info.plist') and n.count('/') == 2]
        if len(roots) != 1:
            raise ValueError('expected one primary app bundle')
        root = roots[0]
        info = plistlib.loads(z.read(root+'Info.plist'))
        bundles = []
        for n in sorted(names):
            if not n.endswith('/Info.plist'):
                continue
            base = n[:-10]
            if base != root and not re.search(r'\.(framework|appex)/$', base):
                continue
            d = plistlib.loads(z.read(n))
            exe = base+d.get('CFBundleExecutable','')
            bundles.append({'path': base, 'metadata': {k:d.get(k) for k in ('CFBundleIdentifier','CFBundleDisplayName','CFBundleShortVersionString','CFBundleVersion','MinimumOSVersion')},
                            'executable': exe, 'binary': macho(z.read(exe), z.read(n),z.read(base+'_CodeSignature/CodeResources') if base+'_CodeSignature/CodeResources' in names else None) if exe in names else None})
        dylibs = [{'path':n,'binary':macho(z.read(n))} for n in sorted(names) if n.endswith('.dylib')]
        loader = root+'Frameworks/libloader.framework/libloader'
        b = z.read(loader)
        needles = [b'com.i3rby.8poolmod.autobreak.illegal.v1', b'com.i3rby.8poolmod.autoqueue.tiercode.v1', b'com.i3rby.autoplay', b'Aim Mode', b'Aim Strength', b'Max Aim Speed', b'GBModMenuDelegate', b'Free Auto Queue time', b'activate a key in Account']
        strings = []
        for needle in needles:
            at = b.find(needle)
            if at >= 0:
                strings.append({'needle':needle.decode(),'offset':at,'excerpt':b[at:at+180].split(b'\0')[0].decode(errors='replace')})
        out = {'method':'stdlib ZIP/plist/Mach-O/nlist/CodeDirectory/resource-hash inspection; read-only; no binary execution',
               'input': {'path':str(path.resolve()),'size_bytes':path.stat().st_size,'sha256_before':before,'zip_entries':len(z.infolist()),'zip_crc':'PASS'},
               'application_metadata':info, 'bundles':bundles,'dynamic_libraries':dylibs,
               'signature_resource_seals':[s for s in (seal(z,x['path'],names) for x in bundles) if s],
               'selected_loader_strings':strings,'provisioning_paths':[n for n in sorted(names) if n.endswith('.mobileprovision')],
               'sc_info_paths':[n for n in sorted(names) if '/SC_Info/' in n],
               'resource_inventory':dict(collections.Counter(Path(n).suffix for n in names if not n.endswith('/'))),
               'localization_directories':sorted(set(p for n in names for p in n.split('/') if p.endswith('.lproj'))),
               'runtime_execution':'NOT TESTED', 'cms_trust_validation':'NOT TESTED'}
    out['input']['sha256_after'] = digest(path.read_bytes())
    out['input']['unchanged'] = before == out['input']['sha256_after']
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('ipa',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    data = inspect(a.ipa)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(data['input'],indent=2))


if __name__ == '__main__':
    main()
