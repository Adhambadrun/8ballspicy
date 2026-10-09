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

Reporting rules
---------------
``FAIL``  the term is not present at the cited offset at all.
``WARN``  the term is present only with different letter case. Offsets are
          still correct, but the quoted evidence does not reproduce the bytes
          verbatim, so the citation should be corrected.
``PASS``  the exact quoted bytes are present at the cited offset.

Presence of a string never proves a feature works, and absence never proves a
feature is missing. This tool verifies citations, not functionality.
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


def audit(ipa, matrix_path, evidence_path):
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

    return {
        'method': 'Read-only re-derivation of matrix citations from the immutable IPA; '
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
    p.add_argument('--output', type=Path, default=None)
    a = p.parse_args()

    result = audit(a.ipa, a.matrix, a.evidence)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')

    print(f"loader sha256 : {result['loader']['sha256']}")
    print(f"categories    : {result['advertised_categories']}")
    print(f"citations     : {result['summary']}")
    for f in result['findings']:
        if f['result'] != 'PASS':
            print(f"  {f['result']}: {f['detail']}")
    print('RESULT:', 'PASS' if result['passed'] else 'FAIL')
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
