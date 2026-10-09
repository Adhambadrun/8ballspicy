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

## Independent component — not an IPA

Existing `MrSpicyUI-iphoneos-arm64-unsigned.zip` packages contain a real arm64
Mach-O **relocatable object**, Swift module and component resource bundle.
They require source-level integration and a complete host build/signing
process; they cannot be sideloaded as a game/app IPA. Source: `../MrSpicyUI/`;
UIKit test host: `../HostApp/` (**not 8 Ball Pool**).

Latest current component evidence, source/run IDs and independently calculated
hash are recorded in `../validation/manifests/release-manifest.json` and
`../validation/reports/build-and-signing-report.md` after CI verification.

Verified historical fallback (before current repairs):
`ci/artifacts:runs/37916687975-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip`,
SHA-256 `2d34b9d00c8f3aad00ffcf5ec0419a42bf16a8d02ba4c8b702966ba8b3399b2c`.
Git retrieval (no branch switching or game artifact download required):

```bash
git fetch origin ci/artifacts
git show FETCH_HEAD:runs/37916687975-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip \
  > /path/to/MrSpicyUI-iphoneos-arm64-unsigned.zip
sha256sum /path/to/MrSpicyUI-iphoneos-arm64-unsigned.zip
```

No GitHub release exists or was newly created/uploaded in this session.
