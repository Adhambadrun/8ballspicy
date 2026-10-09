# CI workflow is preserved here as text, not installed

`component-ci.workflow.yml.txt` is a verbatim copy of the working GitHub Actions
workflow that builds and tests `MrSpicyUI` on a macOS runner, taken from
`.github/workflows/component-ci.yml` at `08937925a` on `abadrun/8ballspicy`
(branch `arena/6264dd0a-8ballspicy`) — the source of record.

It defines three jobs: `component` (forensic parser unit tests, read-only Apple
inspection of the immutable input, toolchain record, hostless simulator tests,
unsigned `generic/platform=iOS` arm64 build, architecture verification,
package + hash, provenance, artifact upload), `hosted-tests` (the same test
sources inside the real `UIApplicationMain` host, plus a repeat pass of the
animated-transition regressions), and `publish-evidence` (writes the verified
logs and artifact back to the session branch).

The copy is byte-identical to the source of record except that it is stored
under a `.txt` name. An earlier copy in this directory carried this session's
branch name in two places; it was replaced with the authoritative version so
that only one workflow definition is in the repository.

It is stored as `.txt` in this directory — **not** under `.github/workflows/` —
because the GitHub App token available to this session was rejected when pushing
any commit that creates or updates a workflow file:

```
! [remote rejected] (refusing to allow a GitHub App to create or update workflow
  `.github/workflows/component-ci.yml` without `workflows` permission)
```

Consequences, stated plainly:

* This session branch (`arena/627c356f-8ballspicy` on `Adhambadrun/8ballspicy`)
  **cannot run the macOS component CI itself**, and therefore cannot produce its
  own new build/test evidence.
* All build and test evidence cited by this session was produced by runs on
  `abadrun/8ballspicy` and was **independently re-verified** here: artifact ZIPs
  were downloaded, their SHA-256 recomputed and compared to the recorded values,
  the Mach-O outputs re-parsed, and the raw `xcodebuild` logs re-read for the
  actual executed / failed / skipped counts.
* To re-enable CI on a branch, a maintainer with the `workflows` scope must copy
  this file to `.github/workflows/component-ci.yml` and update the two references
  to the session branch name (the `on.push.branches` filter and the
  `test "$SESSION_BRANCH" = ...` guard in the publish job).

The workflow only builds and tests the independent `MrSpicyUI` component and
performs read-only static inspection of the input IPA. It never modifies,
re-signs, or repackages the 8 Ball Pool application.
