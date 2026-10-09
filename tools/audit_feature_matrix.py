#!/usr/bin/env python3
"""Re-derive the advertised-feature evidence directly from the immutable IPA.

The 42-category matrix in ``validation/reports/feature-verification-matrix.md``
cites exact byte offsets inside
``Payload/pool.app/Frameworks/libloader.framework/libloader``. This tool
re-reads those bytes and independently confirms every citation, so the matrix
stays auditable instead of being a static claim.

Checks performed
----------------
1. The loader binary SHA-256 equals the value recorded in the evidence JSON.
2. Every ``hits`` entry in the evidence JSON resolves to its recorded offset.
3. Every ```term` @ offset`` citation in the markdown matrix resolves.
4. The matrix and the evidence JSON describe the same 42 features.
5. Rows stating "No match" correspond to evidence features with zero hits.
6. No row advertises a game-only feature as implemented or available.
7. Every matrix row has exactly one status-taxonomy assignment, and the
   assignment is compatible with the row's final status
   (``validation/evidence/feature-status-taxonomy.json``).
8. Every row that claims Mr. Spicy-side support (``ui-only`` or
   ``implemented (component only)``) cites component source files that exist
   and contain the evidence token; no game-only row may carry such evidence
   (``validation/evidence/component-feature-evidence.json``).

Reporting rules
---------------
``FAIL``  the term is not present at the cited offset at all.
``WARN``  the term is present only with different letter case. Offsets are
          still correct, but the quoted evidence does not reproduce the bytes
          verbatim, so the citation should be corrected.
``PASS``  the exact quoted bytes are present at the cited offset.

Presence of a string never proves a feature works, and absence never proves a
feature is missing. This tool verifies citations and evidence links, not
functionality.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

LOADER = 'Payload/pool.app/Frameworks/libloader.framework/libloader'
EXPECTED_LOADER_SHA256 = 'bc6e41931e80a1fb7832612626ac05aacc7a45ecfbe7d73b45adbb889929823a'
CITATION = re.compile(r'`([^`]+)` @ (\d+)')
MATRIX_HEADER = '| Feature |'
DEFAULT_TAXONOMY = 'validation/evidence/feature-status-taxonomy.json'
DEFAULT_COMPONENT_EVIDENCE = 'validation/evidence/component-feature-evidence.json'

# The seven status categories used in the matrix. Their meaning is defined in
# validation/reports/feature-verification-matrix.md ("Status taxonomy").
TAXONOMY = (
    'Implemented and tested',
    'Implemented but incompletely tested',
    'UI representation only',
    'Explicitly unavailable',
    'Blocked by host integration',
    'Dependent on external authorization',
    'Not implemented',
)

# Which taxonomy categories a final status may map to. A row can never be
# labelled "Implemented and tested" unless its status says the component (or
# game) implements it, and no game-only status can map to an implemented category.
ALLOWED_CATEGORIES_BY_STATUS = {
    'unavailable': ('Explicitly unavailable', 'Blocked by host integration', 'Not implemented'),
    'ui-only': ('UI representation only',),
    'awaiting verification': ('Dependent on external authorization',),
    'implemented (component only)': ('Implemented but incompletely tested',),
}

# Statuses that assert some Mr. Spicy-side support and therefore need component
# source evidence. Game-only ("unavailable") rows must not carry such evidence.
COMPONENT_EVIDENCE_STATUSES = ('ui-only', 'implemented (component only)')


def matrix_rows(text):
    """Return the feature rows of the main matrix table as cell lists."""
    rows, in_table = [], False
    for line in text.splitlines():
        if line.startswith(MATRIX_HEADER):
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


def read_loader(ipa):
    with zipfile.ZipFile(ipa) as z:
        return z.read(LOADER)


def check(term, offset, blob):
    """Return 'PASS', 'WARN' (case drift) or 'FAIL' for one citation."""
    raw = term.encode()
    at = int(offset)
    if blob[at:at + len(raw)] == raw:
        return 'PASS'
    if blob[at:at + len(raw)].decode('utf-8', 'replace').lower() == term.lower():
        return 'WARN'
    return 'FAIL'


def check_taxonomy(rows, taxonomy, record):
    """Every row has one assignment, and each assignment fits the row's status."""
    if taxonomy.get('categories') != list(TAXONOMY):
        record('FAIL', 'taxonomy categories differ from the seven defined categories',
               check='taxonomy_categories', found=taxonomy.get('categories'))
    else:
        record('PASS', 'taxonomy defines exactly the seven status categories',
               check='taxonomy_categories')

    assignments = taxonomy.get('assignments', {})
    names = [r[0] for r in rows]
    missing = [n for n in names if n not in assignments]
    extra = sorted(n for n in assignments if n not in names)
    if missing or extra or len(set(names)) != len(names):
        record('FAIL', 'taxonomy assignments do not cover each matrix row exactly once',
               check='taxonomy_coverage', missing=missing, extra=extra)
    else:
        record('PASS', f'every one of the {len(rows)} matrix rows has exactly one taxonomy assignment',
               check='taxonomy_coverage', count=len(rows))

    contradictions = []
    for row in rows:
        name, status = row[0], row[-1]
        category = assignments.get(name)
        allowed = ALLOWED_CATEGORIES_BY_STATUS.get(status.lower(), ())
        if category not in TAXONOMY or category not in allowed:
            contradictions.append({'feature': name, 'status': status, 'category': category})
    if contradictions:
        record('FAIL', 'taxonomy category contradicts the final status of a row',
               check='taxonomy_status_consistency', rows=contradictions)
    else:
        record('PASS', 'every taxonomy category is compatible with its row status',
               check='taxonomy_status_consistency')


def check_component_evidence(rows, spec, root, record):
    """Support claims need component source evidence; game-only rows may not carry it."""
    features = spec.get('features', {})
    names = {r[0] for r in rows}
    statuses = {r[0]: r[-1].lower() for r in rows}

    stray = sorted(n for n in features if n not in names
                   or statuses[n] not in COMPONENT_EVIDENCE_STATUSES)
    if stray:
        record('FAIL', 'component evidence is attached to a row that does not claim Mr. Spicy-side support',
               check='component_evidence_scope', rows=stray)
    else:
        record('PASS', 'component evidence is attached only to rows that claim Mr. Spicy-side support',
               check='component_evidence_scope')

    unsupported, unresolved = [], []
    for row in rows:
        name, status = row[0], row[-1].lower()
        if status not in COMPONENT_EVIDENCE_STATUSES:
            continue
        entries = features.get(name, [])
        if not entries:
            unsupported.append(name)
            continue
        for entry in entries:
            source = Path(root) / entry['file']
            if not source.exists():
                unresolved.append({'feature': name, 'file': entry['file'], 'reason': 'file missing'})
                continue
            text = source.read_text(encoding='utf-8', errors='replace')
            if entry['contains'] not in text:
                unresolved.append({'feature': name, 'file': entry['file'],
                                   'reason': 'evidence token not found', 'token': entry['contains']})
    if unsupported or unresolved:
        record('FAIL', 'a row claims Mr. Spicy-side support without resolvable component evidence',
               check='component_evidence_resolves', unsupported=unsupported, unresolved=unresolved)
    else:
        supported = [r[0] for r in rows if r[-1].lower() in COMPONENT_EVIDENCE_STATUSES]
        record('PASS', f'{len(supported)} component-supported row(s) cite component source that contains their evidence',
               check='component_evidence_resolves', rows=supported)


def audit(ipa, matrix_path, evidence_path, taxonomy_path=None,
          component_evidence_path=None, root=None):
    root = Path(root) if root is not None else Path('.')
    taxonomy_path = Path(taxonomy_path) if taxonomy_path is not None else root / DEFAULT_TAXONOMY
    component_evidence_path = (Path(component_evidence_path) if component_evidence_path is not None
                               else root / DEFAULT_COMPONENT_EVIDENCE)
    blob = read_loader(ipa)
    sha = hashlib.sha256(blob).hexdigest()
    evidence = json.loads(Path(evidence_path).read_text(encoding='utf-8'))
    matrix_text = Path(matrix_path).read_text(encoding='utf-8')
    rows = matrix_rows(matrix_text)

    findings = []
    counts = {'PASS': 0, 'WARN': 0, 'FAIL': 0}

    def record(kind, detail, **extra):
        counts[kind] += 1
        entry = {'result': kind, **extra}
        findings.append({**entry, 'detail': detail})

    # 1. loader identity
    if sha == EXPECTED_LOADER_SHA256:
        record('PASS', 'loader SHA-256 matches the recorded evidence hash',
               check='loader_sha256', sha256=sha)
    else:
        record('FAIL', 'loader SHA-256 does not match the recorded evidence hash',
               check='loader_sha256', sha256=sha, expected=EXPECTED_LOADER_SHA256)

    recorded_sha = evidence.get('binary_sha256')
    if recorded_sha == sha:
        record('PASS', 'evidence JSON binary_sha256 matches the IPA bytes',
               check='evidence_binary_sha256')
    else:
        record('FAIL', 'evidence JSON binary_sha256 does not match the IPA bytes',
               check='evidence_binary_sha256', recorded=recorded_sha, observed=sha)

    # 2. evidence JSON hits
    for feature in evidence.get('features', []):
        for hit in feature.get('hits', []):
            result = check(hit['term'], hit['offset'], blob)
            record(result,
                   f"{feature['feature']}: evidence hit {hit['term']!r} @ {hit['offset']}",
                   check='evidence_hit', feature=feature['feature'],
                   term=hit['term'], offset=hit['offset'])

    # 3. markdown citations
    for term, offset in CITATION.findall(matrix_text):
        result = check(term, offset, blob)
        record(result, f'matrix citation {term!r} @ {offset}',
               check='matrix_citation', term=term, offset=int(offset))

    # 4. same feature population
    evidence_names = [f['feature'] for f in evidence.get('features', [])]
    matrix_names = [r[0] for r in rows]
    if evidence_names == matrix_names:
        record('PASS', f'matrix and evidence describe the same {len(rows)} features',
               check='feature_population', count=len(rows))
    else:
        record('FAIL', 'matrix and evidence feature lists diverged',
               check='feature_population', matrix=matrix_names, evidence=evidence_names)

    if len(rows) == 42:
        record('PASS', 'matrix contains exactly 42 advertised categories',
               check='advertised_category_count', count=len(rows))
    else:
        record('FAIL', f'matrix contains {len(rows)} advertised categories, expected 42',
               check='advertised_category_count', count=len(rows))

    # 5. "no match" rows agree with zero-hit features
    no_match_rows = {r[0] for r in rows if 'No match' in ' '.join(r)}
    zero_hit_features = {f['feature'] for f in evidence.get('features', []) if not f.get('hits')}
    if no_match_rows == zero_hit_features:
        record('PASS', 'every "No match" row corresponds to a zero-hit evidence feature',
               check='no_match_consistency', features=sorted(no_match_rows))
    else:
        record('FAIL', '"No match" rows and zero-hit evidence features diverged',
               check='no_match_consistency', rows=sorted(no_match_rows),
               evidence=sorted(zero_hit_features))

    # 6. no game-only feature advertised as working
    status_index = len(rows[0]) - 1 if rows else -1
    dishonest = []
    for row in rows:
        status = row[status_index].lower() if status_index >= 0 else ''
        if status in ('unavailable', 'ui-only', 'awaiting verification') or status.startswith('implemented (component only)'):
            continue
        dishonest.append({'feature': row[0], 'status': row[status_index]})
    if not dishonest:
        record('PASS', 'no advertised feature is reported as implemented in the game',
               check='feature_status_honesty')
    else:
        record('FAIL', 'feature rows claim an unsupported implementation status',
               check='feature_status_honesty', rows=dishonest)

    # 7-8. status taxonomy and component evidence
    taxonomy = json.loads(taxonomy_path.read_text(encoding='utf-8')) if taxonomy_path.exists() else None
    if taxonomy is None:
        record('FAIL', f'taxonomy file {taxonomy_path} is missing', check='taxonomy_present')
    else:
        check_taxonomy(rows, taxonomy, record)

    spec = (json.loads(component_evidence_path.read_text(encoding='utf-8'))
            if component_evidence_path.exists() else None)
    if spec is None:
        record('FAIL', f'component evidence file {component_evidence_path} is missing',
               check='component_evidence_present')
    else:
        check_component_evidence(rows, spec, root, record)

    return {
        'method': 'Read-only re-derivation of matrix citations from the immutable IPA; '
                  'component evidence links resolved against the working tree; '
                  'no game execution, patching or redistribution.',
        'loader': {'path': LOADER, 'size_bytes': len(blob), 'sha256': sha},
        'matrix': str(matrix_path),
        'evidence': str(evidence_path),
        'advertised_categories': len(rows),
        'summary': counts,
        'passed': counts['FAIL'] == 0,
        'findings': findings,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--ipa', type=Path, default=Path('pool8Signed.ipa'))
    p.add_argument('--matrix', type=Path,
                   default=Path('validation/reports/feature-verification-matrix.md'))
    p.add_argument('--evidence', type=Path,
                   default=Path('validation/evidence/feature-string-search.json'))
    p.add_argument('--taxonomy', type=Path, default=Path(DEFAULT_TAXONOMY))
    p.add_argument('--component-evidence', type=Path, default=Path(DEFAULT_COMPONENT_EVIDENCE))
    p.add_argument('--root', type=Path, default=Path('.'),
                   help='repository root that component evidence paths are relative to')
    p.add_argument('--output', type=Path, default=None)
    a = p.parse_args()

    result = audit(a.ipa, a.matrix, a.evidence, a.taxonomy, a.component_evidence, a.root)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')

    print(f"loader sha256 : {result['loader']['sha256']}")
    print(f"categories    : {result['advertised_categories']}")
    print(f"findings      : {result['summary']}")
    for f in result['findings']:
        if f['result'] != 'PASS':
            print(f"  {f['result']}: {f['detail']}")
    print('RESULT:', 'PASS' if result['passed'] else 'FAIL')
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
