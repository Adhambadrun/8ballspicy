# output/

**No release IPA is present here, on purpose.**

The mission's expected release artifacts at `output/Mr Spicy.ipa` and
`output/Mr Spicy.sha256` are defined as the *integrated, signed* 8 Ball Pool
build containing the Mr. Spicy UI. Producing that artifact requires:

1. owner-authorized host source (or an official integration interface) for
   `com.miniclip.8ballpoolmult`, and
2. an Apple-issued signing identity + provisioning profile for a legitimate
   export.

Neither exists in any reachable environment (evidence:
`../validation/reports/integration-validation.md`). Creating an empty,
unsigned, renamed, or otherwise placeholder file at the expected paths would
be a fake release and is prohibited by the mission — so the paths are left
empty.

**What was actually produced and verified** (see
`../validation/manifests/release-manifest.json` for hashes):

- `MrSpicyUI-iphoneos-arm64-unsigned.zip` — device-architecture (arm64,
  iphoneos SDK 26.5) component build, SHA-256
  `1a57bab96031dc78abde5eec594eb8ca9f1121ebc47819a67cd2ed7df97c034d`,
  stored on the repository's `ci/artifacts` branch under
  `runs/37915278092-component/dist/` (1.7 MB, regenerable via CI).
- Component sources: `../MrSpicyUI/` (version 1.0.0).
- Test host app: `../HostApp/MrSpicyDemoHost` (component test host — **not**
  the game).
- CI logs and results: `ci/artifacts` branch.
