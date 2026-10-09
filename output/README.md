# Delivery status

**`output/pool8Signed.ipa — NOT PRODUCED`**

**`output/pool8Signed.sha256 — NOT PRODUCED`**

No placeholder, renamed demo, unsigned IPA, or game release was created.
The immutable input remains `/home/user/8ballspicy/pool8Signed.ipa`:
**99,010,014 bytes**, SHA-256
`6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84`,
ZIP CRC PASS, 3,527 entries. Identity: **8 Ball Pool** /
**com.miniclip.8ballpoolmult**, **56.31.0 / 5330**, iOS13/arm64.
Unchanged bytes do not establish clean provenance or normal game behavior.

## Delivered independent component — not an IPA

- Continued/repaired Swift/UIKit source: `../MrSpicyUI/`; demo/test host:
  `../HostApp/` (**not the game**). Existing generated S mark reused, not
  recovered historical artwork.
- Verified source: `fae2937905395c425c777c38cbc05e115b2e1d71`.
- [Workflow 37928629998: SUCCESS](https://github.com/abadrun/8ballspicy/actions/runs/37928629998) — 51 hosted passes; hostless
  34 passes / 17 explicit skips; ten repeated animation passes; four parser tests.
- [Unsigned arm64 component ZIP](https://github.com/abadrun/8ballspicy/blob/dbc070bba16c4d9b5deba7fed2e6e97ed0365c30/validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip)
  at `../validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip`; **1,729,023 bytes**.
- SHA-256: `3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6`.
- ZIP CRC / source provenance / arm64 MH_OBJECT independently verified.
  Contains object/module/resources, **not an installable app or signed archive**.

```bash
# From the repository root, no branch switching required:
python3 tools/verify_component_evidence.py 37928629998 \
  --output /tmp/component-verification.json
sha256sum validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip
```

## Reports and exact next steps

- [Forensics](../validation/reports/forensic-analysis.md): Apple input signature
  verification FAILED; stale code/resource seals and unsigned mod-related loader.
- [42-category feature audit](../validation/reports/feature-verification-matrix.md)
- [Build/tests/signing](../validation/reports/build-and-signing-report.md)
- [Integration blockers](../validation/reports/integration-validation.md)
- [Device-test status](../validation/reports/device-test-report.md)
- [Machine-readable manifest](../validation/manifests/release-manifest.json)

Actual host integration, Pro authorization, game-wide ad-free, signing/export,
and physical-device tests are **not completed**. MR. SPICY adds no ad code;
preferences store/notify only, with explicit unavailable Pro disclosure.

Proceed only with owner-authorized buildable game source/official SDK and
written UI scope, a clean owner baseline, legitimate Pro/ad-free APIs and test
access, matching Apple identity/profiles for the app and four extensions via
secure tooling, and an authorized physical iOS test device. Preserve original
name/bundle/screens/gameplay; eventual final basename remains **pool8Signed.ipa**.
No GitHub release was created; component evidence is published on the session
branch, not represented as a game release.
