# Output contract

**`output/pool8Signed.ipa — NOT PRODUCED`**
**`output/pool8Signed.sha256 — NOT PRODUCED`**

The original `/home/user/8ballspicy/pool8Signed.ipa` remains immutable input
evidence. An eventual authorized integrated, signed host must remain **8 Ball
Pool**, **com.miniclip.8ballpoolmult**, with exactly the basename
**pool8Signed.ipa** in this separate directory. The former `Mr Spicy.ipa`
output contract was incorrect and is superseded. No placeholder or renamed
demo has been made.

Actual host source/SDK authorization and signing prerequisites are missing;
see `../validation/reports/integration-validation.md` for exact next steps.
Pro is not unlocked, and game ads have not been removed or verified absent.

### Why the input cannot be a legitimate base — decisive evidence

The input is not merely "an IPA we lack permission for"; it is verifiably a
pirated, DRM-stripped, cheat-injected dump, and Apple's own tooling says its
signature is invalid:

* `codesign --verify --deep --strict` (run on a macOS runner, CI 37928629998) →
  **exit 1**, `Payload/pool.app: invalid Info.plist (plist or signature have been modified)`.
* `Info.plist` carries **`DecryptedBy = "@FastDecryptBot - https://t.me/FastDecryptBot"`**.
* `LC_ENCRYPTION_INFO_64` present with **`cryptid=0`** (FairPlay decrypted);
  **61** `SC_Info` FairPlay artifacts missing from the seal.
* An injected `LC_LOAD_DYLIB` pulls in `Frameworks/libloader.framework/libloader`
  (12,265,804 B, **no code signature**, bundle id `com.appdome.libloader`) whose
  strings are a cheat menu: `Aim Mode`, `Aim Strength`, `Max Aim Speed`,
  `Prediction Lines`, `Pocket Hints`, `Auto Play`, `Humanization`,
  `com.i3rby.8poolmod.autobreak.illegal.v1`, PRO-key/Telegram activation.
* Git history shows the prior filename `8-ball-pool-i3rby-IPAOMTK.COM.ipa`.
* `embedded.mobileprovision` is absent everywhere, so it is not installable as-is.

Re-signing and redistributing it would require circumventing FairPlay and Apple
code signing on a third party's copyrighted game, and would ship cheat
functionality into a live competitive multiplayer game. That is refused on
legitimacy grounds, independent of the missing macOS/Xcode/signing toolchain.
Details: `../validation/reports/forensic-analysis.md`.

## Independent component — not an IPA

Existing `MrSpicyUI-iphoneos-arm64-unsigned.zip` packages contain a real arm64
Mach-O **relocatable object**, Swift module and component resource bundle.
They require source-level integration and a complete host build/signing
process; they cannot be sideloaded as a game/app IPA. Source: `../MrSpicyUI/`;
UIKit test host: `../HostApp/` (**not 8 Ball Pool**).

## Current verified component artifact

CI run **37928629998** (`abadrun/8ballspicy`, branch `arena/6264dd0a-8ballspicy`,
source commit `fae2937905395c425c777c38cbc05e115b2e1d71`) completed **success**:

| Check | Result |
|---|---|
| Hosted UIApplication tests | **51 executed, 0 failures, 0 skipped** — TEST SUCCEEDED |
| Hostless package tests | **51 executed, 0 failures, 17 skipped** — TEST SUCCEEDED |
| Animated-transition repeat | **10 executed, 0 failures** — TEST SUCCEEDED |
| arm64 device build | succeeded (`generic/platform=iOS`, Release, `CODE_SIGNING_ALLOWED=NO`) |
| Signature | **unsigned by design** — no Apple identity exists in this environment |

Artifact, SHA-256 recomputed independently from the downloaded bytes:

```
MrSpicyUI-iphoneos-arm64-unsigned.zip
  sha256  3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6
  size    1,729,023 bytes
  path    validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip
```

Retrieval (no branch switching and no game-artifact download required):

```bash
git fetch https://github.com/abadrun/8ballspicy.git arena/6264dd0a-8ballspicy
git show FETCH_HEAD:validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip \
  > /path/to/MrSpicyUI-iphoneos-arm64-unsigned.zip
sha256sum /path/to/MrSpicyUI-iphoneos-arm64-unsigned.zip
```

Superseded artifacts from earlier runs remain valid for their own revisions —
`37915278092` → `1a57bab9…` (1,712,887 B), `37916599818` → `1b2d4b17…`
(1,712,888 B), `37916687975` → `2d34b9d0…` (1,712,890 B) — and are mirrored on
the `ci/artifacts` branch of the same repository. They predate the lifecycle
repair and the 33 → 51 test growth, so `3a872657…` is the one to use.

Full evidence, counts and the regression history (including the 8-failure and
1-failure runs that were fixed on the way) are in
`../validation/manifests/release-manifest.json`,
`../validation/reports/build-and-signing-report.md` and
`../validation/evidence/session-627c356f-independent-verification.json`.

No GitHub release exists or was newly created/uploaded in this session.
