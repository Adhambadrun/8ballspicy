#!/usr/bin/env python3
"""Release-integrity gate for the Mr. Spicy x 8 Ball Pool project.

The delivery contract has exactly two artifacts:
``output/pool8Signed.ipa`` and ``output/pool8Signed.sha256``. Until a genuine,
authorized integration has been built, signed and validated, the honest state
is **NOT PRODUCED**. This gate exists so that a missing integration, a failed
test, a renamed demo app, an unsigned component ZIP or a placeholder file can
never be reported as a successful release.

Every check is derived from files that actually exist in the working tree, the
immutable input IPA, or git object IDs. Nothing is taken on trust from a
report. A check that cannot be evaluated reports ``UNVERIFIED`` with the reason
and does not count as a pass or a failure.

Run from the repository root:

    python3 tools/verify_release_state.py
    python3 tools/verify_release_state.py --output validation/evidence/release-state.json
"""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import zipfile
from pathlib import Path

INPUT_IPA = 'pool8Signed.ipa'
INPUT_SHA256 = '6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84'
INPUT_SIZE = 99010014
OUTPUT_IPA = 'output/pool8Signed.ipa'
OUTPUT_SHA = 'output/pool8Signed.sha256'
MANIFEST = 'validation/manifests/release-manifest.json'
MATRIX = 'validation/reports/feature-verification-matrix.md'
LOADER = 'Payload/pool.app/Frameworks/libloader.framework/libloader'
BRAND_MARK = 'MrSpicyUI/Sources/MrSpicyUI/Resources/Branding/spicy-s-mark.png'
COMPONENT_SOURCES = ('MrSpicyUI/Sources', 'HostApp')
SOURCE_TREES = ('MrSpicyUI', 'HostApp', 'tools')

# Honest per-feature statuses. Anything else means a row is advertising a
# capability the project has not established.
HONEST_STATUSES = ('unavailable', 'ui-only', 'awaiting verification', 'implemented (component only)')

# Material that must never appear in the component or its test host: advertising
# SDKs, networking clients, or dynamic-loading tricks used to reach into a host.
FORBIDDEN_SOURCE_PATTERNS = (
    'applovin', 'adsurge', 'bigoads', 'dtbios', 'fbaudiencenetwork', 'inmobi',
    'moloco', 'omsdk', 'googleadsondeviceconversion', 'admob', 'gadinterstitial',
    'urlsession', 'nwconnection', 'nsurlconnection', 'cfnetwork',
    'libloader', 'dlopen', 'dlsym', 'dladdr', 'mach_header', 'dyld_interpose',
    'mshookfunction', 'substrate', 'cycript',
)

# Pro must stay a read-only disclosure. Any entitlement, purchase or unlock API in
# the component or host would let the UI represent Pro as authorized without a
# real entitlement signal, so none may appear in the component or host sources.
PRO_ENTITLEMENT_PATTERNS = (
    'storekit', 'skpayment', 'skproduct', 'currententitlements', 'appstorereceipt',
    'entitlement', 'unlockpro', 'proenabled', 'isprouser', 'skreceiptrefresh',
)

# Repository root the checks run against. Tests point this at a temporary tree.
ROOT = Path('.')


def path(rel):
    """Resolve a repository-relative path against `ROOT`."""
    return ROOT / rel


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    proc = subprocess.run(('git',) + args, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def matrix_feature_rows(text):
    """Return the feature rows of the main matrix table as cell lists."""
    rows, in_table = [], False
    for line in text.splitlines():
        if line.startswith('| Feature |'):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith('|'):
            break
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells or all(set(c) <= set('-: ') for c in cells):
            continue
        rows.append(cells)
    return rows


class Report:
    """Collects check results. `FAIL` is the only outcome that fails the gate."""

    def __init__(self):
        self.checks = []

    def add(self, name, result, detail, **extra):
        self.checks.append({'check': name, 'result': result, 'detail': detail, **extra})

    def ok(self, name, detail, **extra):
        self.add(name, 'PASS', detail, **extra)

    def fail(self, name, detail, **extra):
        self.add(name, 'FAIL', detail, **extra)

    def warn(self, name, detail, **extra):
        self.add(name, 'WARN', detail, **extra)

    def unverified(self, name, detail, **extra):
        self.add(name, 'UNVERIFIED', detail, **extra)

    def result(self, name):
        for c in self.checks:
            if c['check'] == name:
                return c['result']
        return None

    @property
    def counts(self):
        out = {}
        for c in self.checks:
            out[c['result']] = out.get(c['result'], 0) + 1
        return out

    @property
    def passed(self):
        return not any(c['result'] == 'FAIL' for c in self.checks)


# --------------------------------------------------------------------------
# Individual checks
# --------------------------------------------------------------------------

def check_input_immutable(r):
    ipa = path(INPUT_IPA)
    if not ipa.exists():
        r.fail('input_ipa_present', f'{INPUT_IPA} is missing')
        return None
    size = ipa.stat().st_size
    digest = sha256_file(ipa)
    try:
        with zipfile.ZipFile(ipa) as z:
            bad = z.testzip()
            entries = len(z.infolist())
            loader = z.read(LOADER)
            loader_sha = hashlib.sha256(loader).hexdigest()
    except Exception as exc:  # noqa: BLE001 - reported, not raised
        r.fail('input_ipa_readable', f'cannot read {INPUT_IPA}: {exc}')
        return None
    if bad is not None:
        r.fail('input_zip_crc', f'ZIP CRC failure at {bad}')
    else:
        r.ok('input_zip_crc', 'ZIP CRC PASS', entries=entries)
    if size == INPUT_SIZE and digest == INPUT_SHA256:
        r.ok('input_ipa_unchanged',
             'input IPA size and SHA-256 match the immutable record',
             size_bytes=size, sha256=digest, entries=entries)
    else:
        r.fail('input_ipa_unchanged',
               'input IPA differs from the immutable record',
               size_bytes=size, expected_size=INPUT_SIZE,
               sha256=digest, expected_sha256=INPUT_SHA256)
    return {'entries': entries, 'loader_sha256': loader_sha, 'loader_size_bytes': len(loader)}


def check_release_not_produced(r):
    """The release artifacts must not exist unless integration truly happened."""
    produced = [p for p in (path(OUTPUT_IPA), path(OUTPUT_SHA)) if p.exists()]
    out_dir = path('output')
    stray = sorted(str(p.relative_to(out_dir))
                   for p in out_dir.rglob('*')
                   if p.is_file() and p.name != 'README.md') if out_dir.exists() else []
    if produced or stray:
        r.fail('release_ipa_not_produced',
               'output/ contains files other than README.md',
               produced=[str(p) for p in produced], stray=stray)
    else:
        r.ok('release_ipa_not_produced',
             'output/pool8Signed.ipa and output/pool8Signed.sha256 are absent; '
             'output/ holds only README.md (status NOT PRODUCED)')


def check_no_placeholder_release(r):
    """Nothing anywhere may impersonate the game or the release."""
    problems = []
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.git/' in str(p):
            continue
        rel = str(p.relative_to(ROOT))
        if rel == INPUT_IPA:
            continue
        if rel.endswith('.ipa'):
            problems.append({'path': rel, 'reason': 'an .ipa file other than the immutable input'})
        if rel.endswith('.app') or '/Payload/' in rel:
            problems.append({'path': rel, 'reason': 'app bundle / Payload directory'})
        if rel.endswith('.mobileprovision'):
            problems.append({'path': rel, 'reason': 'provisioning profile'})
    if problems:
        r.fail('no_placeholder_release', 'files that could be mistaken for a release',
               problems=problems)
    else:
        r.ok('no_placeholder_release',
             'no .ipa, app bundle, Payload tree or provisioning profile other than '
             'the immutable input')


def check_component_artifacts(r):
    runs = sorted(path('validation/ci/runs').glob('*-component'))
    if not runs:
        r.unverified('component_artifact_hashes', 'no CI run directories present to verify')
        return
    for run in runs:
        zip_path = run / 'dist' / 'MrSpicyUI-iphoneos-arm64-unsigned.zip'
        prov_path = run / 'provenance.json'
        if not zip_path.exists() or not prov_path.exists():
            r.warn(f'component_artifact[{run.name}]',
                   'artifact or provenance missing for this run',
                   path=str(zip_path))
            continue
        prov = json.loads(prov_path.read_text(encoding='utf-8'))
        recorded = (prov.get('artifacts') or [{}])[0]
        digest = sha256_file(zip_path)
        size = zip_path.stat().st_size
        if digest != recorded.get('sha256') or size != recorded.get('size_bytes'):
            r.fail(f'component_artifact[{run.name}]',
                   'artifact hash/size disagree with recorded provenance',
                   path=str(zip_path), sha256=digest, recorded=recorded)
            continue
        with zipfile.ZipFile(zip_path) as z:
            if z.testzip() is not None:
                r.fail(f'component_artifact[{run.name}]', 'artifact ZIP CRC failed',
                       path=str(zip_path))
                continue
            names = z.namelist()
            if 'MrSpicyUI.o' not in names:
                r.fail(f'component_artifact[{run.name}]',
                       'relocatable object missing from the package', entries=names)
                continue
            header = struct.unpack_from('<8I', z.read('MrSpicyUI.o'))
            mach_o = ('thin arm64 MH_OBJECT (relocatable component)'
                      if header[0] == 0xfeedfacf and header[1] == 0x100000c and header[3] == 1
                      else f'unexpected Mach-O (magic={hex(header[0])}, '
                           f'cputype={hex(header[1])}, filetype={header[3]})')
            if 'MH_OBJECT' not in mach_o:
                r.fail(f'component_artifact[{run.name}]',
                       'component package is not a relocatable object', mach_o=mach_o)
                continue
        if prov.get('source_commit') != prov.get('checked_out_commit'):
            r.fail(f'component_provenance[{run.name}]',
                   'checked-out commit differs from the workflow source commit')
            continue
        r.ok(f'component_artifact[{run.name}]',
             'artifact hash, size, CRC and Mach-O type match recorded provenance',
             path=str(zip_path), size_bytes=size, sha256=digest, mach_o=mach_o,
             source_commit=prov.get('source_commit'))


def check_source_provenance(r):
    """The tree in the working copy must be the tree that was tested in CI."""
    code, out, err = git('-C', str(ROOT), 'rev-parse', 'HEAD')
    if code != 0:
        r.unverified('source_provenance', 'not a git repository', error=err)
        return
    trees = {}
    for tree in SOURCE_TREES:
        code, out, err = git('-C', str(ROOT), 'rev-parse', f'HEAD:{tree}')
        if code != 0:
            r.unverified(f'source_tree[{tree}]', 'path not present in HEAD', error=err)
        else:
            trees[tree] = out
    provs = sorted(path('validation/ci/runs').glob('*/provenance.json'))
    if not provs:
        r.unverified('source_provenance', 'no CI provenance records present')
        return
    verified = 0
    divergent = {}
    for prov_path in provs:
        prov = json.loads(prov_path.read_text(encoding='utf-8'))
        recorded = prov.get('source_trees') or {}
        if recorded and recorded == trees:
            verified += 1
        elif recorded and trees:
            # A historical run legitimately tested a different revision; that is
            # only a problem if it is presented as the current verified source.
            # Record which directories differ so the warning is actionable.
            for tree, oid in recorded.items():
                if trees.get(tree) != oid:
                    divergent.setdefault(tree, set()).update([oid, trees.get(tree)])
            r.warn(f'source_provenance[{prov_path.parent.name}]',
                   'run recorded a different source tree than the working copy',
                   recorded=recorded, working_copy=trees,
                   source_commit=prov.get('source_commit'))
    if verified:
        r.ok('source_provenance',
             f'{verified} CI run(s) recorded exactly the working-copy source trees',
             working_copy_trees=trees, runs_verified=verified)
    elif trees:
        detail = {'working_copy_trees': trees,
                  'divergent_directories': sorted(divergent),
                  'note': 'A differing tree means the tested revision is not the '
                          'current one. Re-run CI to re-establish provenance; '
                          'do not present the old artifact as covering this tree.'}
        r.warn('source_provenance',
               'no CI run recorded the current working-copy trees', **detail)


def check_source_snapshot(r):
    """The manifest must record the source trees that HEAD actually contains.

    The snapshot is trees only, not a commit ID: the manifest is itself committed,
    so it cannot name the commit that contains it. Tree IDs do not change when the
    manifest changes, so the comparison is stable.
    """
    manifest = path(MANIFEST)
    if not manifest.exists():
        return  # manifest_present already reports this
    try:
        m = json.loads(manifest.read_text(encoding='utf-8'))
    except Exception:  # noqa: BLE001 - manifest_parseable already reports this
        return
    code, _, err = git('-C', str(ROOT), 'rev-parse', 'HEAD')
    if code != 0:
        r.unverified('manifest_source_snapshot',
                     'not a git repository; manifest source trees cannot be compared', error=err)
        return
    head = {}
    for tree in SOURCE_TREES:
        code, out, err = git('-C', str(ROOT), 'rev-parse', f'HEAD:{tree}')
        if code != 0:
            r.fail('manifest_source_snapshot', f'source tree {tree} is missing from HEAD', error=err)
            return
        head[tree] = out
    snapshot = m.get('source_tree_snapshot')
    recorded = snapshot.get('trees') if isinstance(snapshot, dict) else None
    if not isinstance(recorded, dict):
        r.fail('manifest_source_snapshot',
               'manifest does not record source_tree_snapshot.trees', head=head)
    elif recorded != head:
        r.fail('manifest_source_snapshot',
               'manifest source trees differ from the trees HEAD contains; update the manifest '
               'in the same commit as the source change',
               recorded=recorded, head=head)
    else:
        r.ok('manifest_source_snapshot',
             'manifest source-tree snapshot matches the trees HEAD contains', trees=head)


def check_manifest_consistency(r, input_info):
    manifest = path(MANIFEST)
    if not manifest.exists():
        r.fail('manifest_present', f'{MANIFEST} is missing')
        return
    try:
        m = json.loads(manifest.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001 - reported, not raised
        r.fail('manifest_parseable', f'cannot parse {MANIFEST}: {exc}')
        return

    release = m.get('release_ipa', {})
    problems = []
    if release.get('status') != 'NOT PRODUCED':
        problems.append(f"release_ipa.status is {release.get('status')!r}")
    if release.get('delivered') is not False:
        problems.append('release_ipa.delivered is not false')
    if release.get('sha256') is not None:
        problems.append('release_ipa.sha256 is not null')
    for key in ('expected_path', 'expected_checksum_path'):
        if key not in release:
            problems.append(f'release_ipa.{key} missing')
    if problems:
        r.fail('manifest_release_status',
               'manifest does not record an undelivered release', problems=problems)
    else:
        r.ok('manifest_release_status',
             'manifest records the release as NOT PRODUCED with a null hash')

    observed_output = path(OUTPUT_IPA).exists() or path(OUTPUT_SHA).exists()
    if observed_output and release.get('delivered') is False:
        r.fail('manifest_matches_filesystem',
               'output artifacts exist while the manifest says the release was not delivered')
    elif not observed_output and release.get('delivered') is False:
        r.ok('manifest_matches_filesystem',
             'manifest release status agrees with the absence of output artifacts')

    inp = m.get('input_evidence', {})
    if input_info and path(INPUT_IPA).exists():
        if inp.get('sha256') != INPUT_SHA256 or inp.get('size_bytes') != INPUT_SIZE:
            r.fail('manifest_input_evidence',
                   'manifest input hash/size disagree with the file',
                   manifest=inp, observed_sha256=INPUT_SHA256, observed_size=INPUT_SIZE)
        else:
            r.ok('manifest_input_evidence',
                 'manifest input hash and size agree with the immutable IPA',
                 sha256=INPUT_SHA256, size_bytes=INPUT_SIZE)

    build = m.get('component', {}).get('device_build', {})
    zip_path = path(build.get('path', ''))
    if zip_path.exists():
        digest = sha256_file(zip_path)
        size = zip_path.stat().st_size
        if digest != build.get('sha256') or size != build.get('size_bytes'):
            r.fail('manifest_component_artifact',
                   'manifest component hash/size disagree with the file',
                   path=str(zip_path), sha256=digest, recorded=build)
        else:
            r.ok('manifest_component_artifact',
                 'manifest component artifact hash and size agree with the file',
                 path=str(zip_path), size_bytes=size, sha256=digest)
        if build.get('installable') is not False:
            r.fail('manifest_component_installable',
                   'manifest must record the component package as not installable')
        else:
            r.ok('manifest_component_installable',
                 'manifest records the component package as not installable')
    else:
        r.unverified('manifest_component_artifact',
                     f'recorded component artifact {zip_path} is not present')

    brand = m.get('component', {}).get('brand_asset', {})
    mark = path(BRAND_MARK)
    if mark.exists() and brand.get('sha256'):
        digest = sha256_file(mark)
        if digest != brand['sha256']:
            r.fail('manifest_brand_asset',
                   'manifest brand-mark hash disagrees with the file',
                   sha256=digest, recorded=brand['sha256'])
        else:
            r.ok('manifest_brand_asset', 'manifest brand-mark hash agrees with the file',
                 sha256=digest)
    else:
        r.unverified('manifest_brand_asset', 'brand mark or recorded hash unavailable')

    sig = m.get('signature_validation', {}).get('input_ipa', {})
    if sig.get('result') == 'FAILED' and sig.get('exit_code') == 1:
        r.ok('manifest_signature_claim',
             'manifest records the Apple input-signature verification failure '
             '(exit 1) rather than claiming a valid signature',
             diagnostic=sig.get('diagnostic'))
    else:
        r.fail('manifest_signature_claim',
               'manifest does not record the actual failed input-signature verification',
               recorded=sig)

    feats = m.get('features', {})
    rows = matrix_feature_rows(path(MATRIX).read_text(encoding='utf-8')) if path(MATRIX).exists() else []
    if feats.get('advertised_categories') == len(rows):
        r.ok('manifest_category_count',
             'manifest advertised-category count agrees with the matrix', count=len(rows))
    else:
        r.fail('manifest_category_count',
               'manifest advertised-category count disagrees with the matrix',
               manifest=feats.get('advertised_categories'), matrix=len(rows))

    for key, expected in (('pro', 'read-only unavailable disclosure'),
                          ('ad_free', 'Component adds no ad SDK'),
                          ('automation', 'Reference only')):
        value = feats.get(key, '')
        if expected.lower() in value.lower():
            r.ok(f'manifest_feature_claim[{key}]',
                 'manifest feature claim stays within the verified scope', claim=value)
        else:
            r.fail(f'manifest_feature_claim[{key}]',
                   'manifest feature claim overstates the verified scope', claim=value)


def check_localization(r):
    en = path('MrSpicyUI/Sources/MrSpicyUI/Resources/en.lproj/Localizable.strings')
    ar = path('MrSpicyUI/Sources/MrSpicyUI/Resources/ar.lproj/Localizable.strings')
    if not (en.exists() and ar.exists()):
        r.fail('localization_tables_present', 'en.lproj and/or ar.lproj strings missing')
        return
    en_text = en.read_text(encoding='utf-8')
    ar_text = ar.read_text(encoding='utf-8')
    en_keys = set(re.findall(r'^"([^"]+)"', en_text, re.M))
    ar_keys = set(re.findall(r'^"([^"]+)"', ar_text, re.M))
    if en_keys == ar_keys:
        r.ok('localization_key_parity',
             'English and Arabic define the same key set', keys=len(en_keys))
    else:
        r.fail('localization_key_parity', 'en/ar key sets diverged',
               missing_in_ar=sorted(en_keys - ar_keys),
               missing_in_en=sorted(ar_keys - en_keys))

    sources = []
    for base in COMPONENT_SOURCES:
        sources += sorted(path(base).rglob('*.swift'))
    referenced = set()
    for source in sources:
        text = source.read_text(encoding='utf-8')
        referenced |= set(re.findall(r'SpicyLocalization\.string\(\s*"([^"\\]+)"', text))
        referenced |= set(re.findall(r'titleKey:\s*"([^"\\]+)"', text))
        # Keys built by interpolation, e.g. "mr.spicy.settings.haptic.\(intensity.rawValue)"
        for prefix in re.findall(r'"((?:mr\.spicy|[a-z0-9._-]*spicy[a-z0-9._-]*)[^"\\]*)\\\(', text):
            referenced |= {k for k in en_keys if k.startswith(prefix)}
    missing = sorted(k for k in referenced if k not in en_keys)
    if missing:
        r.fail('localization_keys_resolve',
               'keys referenced by the component are not defined in en.lproj',
               missing=missing)
    else:
        r.ok('localization_keys_resolve',
             'every key referenced by the component resolves in en.lproj and ar.lproj',
             referenced=len(referenced))

    empty = [k for k in ar_keys
             if not re.search(rf'^"{re.escape(k)}"\s*=\s*"[^"]+"', ar_text, re.M)]
    if empty:
        r.fail('localization_arabic_non_empty', 'Arabic strings are empty', keys=empty)
    else:
        r.ok('localization_arabic_non_empty',
             f'all {len(ar_keys)} Arabic values are non-empty', keys=len(ar_keys))


def check_component_scope(r):
    """The component must not contain advertising, networking or host-loading code."""
    offenders = []
    scanned = 0
    for base in COMPONENT_SOURCES:
        for source in sorted(path(base).rglob('*')):
            if not source.is_file() or source.suffix not in ('.swift', '.h', '.m', '.mm'):
                continue
            scanned += 1
            text = source.read_text(encoding='utf-8', errors='replace').lower()
            for pattern in FORBIDDEN_SOURCE_PATTERNS:
                if pattern in text:
                    offenders.append({'path': str(source.relative_to(ROOT)), 'pattern': pattern})
    if offenders:
        r.fail('component_scope', 'component or host references forbidden material',
               offenders=offenders)
    else:
        r.ok('component_scope',
             f'{scanned} component/host source files contain no advertising SDK, '
             'networking client or dynamic host-loading reference')


def check_pro_entitlement_scope(r):
    """Pro is a read-only disclosure: no entitlement or purchase API may be referenced."""
    offenders = []
    scanned = 0
    for base in COMPONENT_SOURCES:
        for source in sorted(path(base).rglob('*')):
            if not source.is_file() or source.suffix not in ('.swift', '.h', '.m', '.mm'):
                continue
            scanned += 1
            text = source.read_text(encoding='utf-8', errors='replace').lower()
            for pattern in PRO_ENTITLEMENT_PATTERNS:
                if pattern in text:
                    offenders.append({'path': str(source.relative_to(ROOT)), 'pattern': pattern})
    if offenders:
        r.fail('pro_entitlement_scope',
               'component or host references an entitlement or purchase API, so Pro could be '
               'represented as authorized without a verified entitlement signal',
               offenders=offenders)
    else:
        r.ok('pro_entitlement_scope',
             f'{scanned} component/host source files reference no entitlement, purchase or '
             'unlock API; Pro remains a read-only disclosure')


def check_feature_honesty(r):
    matrix = path(MATRIX)
    if not matrix.exists():
        r.fail('feature_matrix_present', f'{MATRIX} is missing')
        return
    rows = matrix_feature_rows(matrix.read_text(encoding='utf-8'))
    if len(rows) != 42:
        r.fail('feature_matrix_count',
               f'matrix has {len(rows)} feature rows, expected 42', count=len(rows))
    else:
        r.ok('feature_matrix_count', 'matrix contains exactly 42 advertised categories',
             count=len(rows))
    status_index = len(rows[0]) - 1 if rows else -1
    dishonest = [{'feature': row[0], 'status': row[status_index]}
                 for row in rows if row[status_index].lower() not in HONEST_STATUSES]
    if dishonest:
        r.fail('feature_matrix_statuses',
               'feature rows advertise an unsupported implementation status', rows=dishonest)
    else:
        tally = {}
        for row in rows:
            tally[row[status_index]] = tally.get(row[status_index], 0) + 1
        r.ok('feature_matrix_statuses',
             'every feature row carries an honest availability status', tally=tally)
    component_only = [row[0] for row in rows
                      if row[status_index] == 'implemented (component only)']
    if sorted(component_only) != ['Arabic menu', 'English menu']:
        r.fail('feature_matrix_component_only_claims',
               'rows marked "implemented (component only)" are not the localization rows',
               rows=component_only)
    else:
        r.ok('feature_matrix_component_only_claims',
             'only the English/Arabic menu rows claim implementation, and only in the '
             'component — no game feature is claimed')


def check_reports_present(r):
    expected = [
        'validation/reports/forensic-analysis.md',
        'validation/reports/build-and-signing-report.md',
        'validation/reports/integration-validation.md',
        'validation/reports/device-test-report.md',
        'validation/reports/feature-verification-matrix.md',
    ]
    missing = [p for p in expected if not path(p).exists()]
    if missing:
        r.fail('reports_present', 'expected reports are missing', missing=missing)
    else:
        r.ok('reports_present', 'all five validation reports are present')


ALL_CHECKS = (
    check_input_immutable,
    check_release_not_produced,
    check_no_placeholder_release,
    check_component_artifacts,
    check_source_provenance,
    check_source_snapshot,
    check_manifest_consistency,
    check_localization,
    check_component_scope,
    check_pro_entitlement_scope,
    check_feature_honesty,
    check_reports_present,
)


def run_checks(root=None):
    """Run every check against `root` and return a `Report`."""
    global ROOT
    previous, ROOT = ROOT, Path(root) if root is not None else Path('.')
    try:
        report = Report()
        input_info = check_input_immutable(report)
        for check in ALL_CHECKS[1:]:
            if check is check_manifest_consistency:
                check(report, input_info)
            else:
                check(report)
        return report
    finally:
        ROOT = previous


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', type=Path, default=Path('.'),
                   help='repository root to verify (default: current directory)')
    p.add_argument('--output', type=Path, default=None,
                   help='write the full JSON report to this path')
    a = p.parse_args()

    global ROOT
    ROOT = a.root
    report = Report()
    input_info = check_input_immutable(report)
    for check in ALL_CHECKS[1:]:
        if check is check_manifest_consistency:
            check(report, input_info)
        else:
            check(report)

    ipa = path(INPUT_IPA)
    result = {
        'method': 'Filesystem, git-object, ZIP and Mach-O verification of the actual '
                  'repository state against the recorded delivery claims. '
                  'UNVERIFIED means a check could not be evaluated, not that it passed.',
        'input_ipa': {'path': str(ipa),
                      'size_bytes': ipa.stat().st_size if ipa.exists() else None,
                      'sha256': sha256_file(ipa) if ipa.exists() else None,
                      'expected_sha256': INPUT_SHA256,
                      'unchanged': bool(ipa.exists() and sha256_file(ipa) == INPUT_SHA256)},
        'release_ipa': {'status': 'NOT PRODUCED',
                        'output_ipa_exists': path(OUTPUT_IPA).exists(),
                        'output_checksum_exists': path(OUTPUT_SHA).exists()},
        'summary': report.counts,
        'passed': report.passed,
        'checks': report.checks,
    }
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')

    for c in report.checks:
        marker = {'PASS': 'ok  ', 'FAIL': 'FAIL', 'WARN': 'warn', 'UNVERIFIED': 'unk '}[c['result']]
        print(f"[{marker}] {c['check']}: {c['detail']}")
        for key in ('problems', 'missing', 'offenders', 'rows', 'stray', 'produced'):
            if c.get(key):
                print(f"         {key}: {json.dumps(c[key], ensure_ascii=False)[:400]}")
    print(f"\nsummary: {report.counts}")
    print('RESULT:', 'PASS' if report.passed else 'FAIL')
    raise SystemExit(0 if report.passed else 1)


if __name__ == '__main__':
    main()
